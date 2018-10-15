from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from django.db import models as django_models
#from django.contrib.auth.decorators import user_passes_test
#from django.shortcuts import render_to_response

from .models import FireDepartment, PoliceDepartment
#from django.template import loader
from django.http import HttpResponse
import os, sys, csv, json, datetime, ckanapi
from bitkeeper1 import models
from pprint import pprint
from collections import OrderedDict
import traceback

from bitkeeper1.parameters.local_parameters import BITKEEPER_SETTINGS_FILE as SETTINGS_FILE

from marshmallow import fields, pre_load, post_load
sys.path.insert(0, '/Users/drw/WPRDC/etl-dev/wprdc-etl') # A path that we need to import code from
import pipeline as pl

class SchemaAtom(pl.BaseSchema):
    class Meta:
        ordered = True

def get_resource_parameter(site,resource_id,parameter,API_key=None):
    try:
        ckan = ckanapi.RemoteCKAN(site, apikey=API_key)
        metadata = ckan.action.resource_show(id=resource_id)
        desired_string = metadata[parameter]
    except:
        raise RuntimeError("Unable to obtain resource parameter '{}' for resource with ID {}".format(parameter,resource_id))

    return desired_string

def get_package_parameter(site,package_id,parameter,API_key=None):
    try:
        ckan = ckanapi.RemoteCKAN(site, apikey=API_key)
        metadata = ckan.action.package_show(id=package_id)
        desired_string = metadata[parameter]
    except:
        raise RuntimeError("Unable to obtain package parameter '{}' for package with ID {}".format(parameter,package_id))

    return desired_string

def find_resource_id(site,package_id,resource_name,API_key=None):
    # Get the resource ID given the package ID and resource name.
    resources = get_package_parameter(site,package_id,'resources',API_key)
    for r in resources:
        if r['name'] == resource_name:
            return r['id']
    return None

def write_to_csv(filename,list_of_dicts,keys):
    with open(filename, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, extrasaction='ignore', lineterminator='\n')
        dict_writer.writeheader()
        dict_writer.writerows(list_of_dicts)

def send_data_to_pipeline(resource_name_base,table_name,schema,list_of_dicts,fields,primary_keys,chunk_size=5000):
    # Taken from github.com/WPRDC/stop-in-the-name-of-data.

    specify_resource_by_name = True
    if specify_resource_by_name:
        kwargs = {'resource_name': 'CONNECT: {}'.format(resource_name_base)}
    #else:
        #kwargs = {'resource_id': ''}

    # Synthesize virtual file to send to the FileConnector
    from tempfile import NamedTemporaryFile
    ntf = NamedTemporaryFile()

    # Save the file path
    target = ntf.name
    field_names = [f['id'] for f in fields]
    write_to_csv(target,list_of_dicts,field_names)

    # Testing temporary named file:
    #ntf.seek(0)
    #with open(target,'r') as g:
    #    print(g.read())

    ntf.seek(0)
    #server = "test-connect"
    server = "production"
    # Code below stolen from prime_ckan/*/open_a_channel() but really from utility_belt/gadgets
    #with open(os.path.dirname(os.path.abspath(__file__))+'/ckan_settings.json') as f: # The path of this file needs to be specified.
    with open(SETTINGS_FILE) as f:
        settings = json.load(f)
    site = settings['loader'][server]['ckan_root_url']
    package_id = settings['loader'][server]['package_id']
    API_key = settings['loader'][server]['ckan_api_key']

    update_method = 'upsert'
    if len(primary_keys) == 0:
        update_method = 'insert'

    clear_first = False
    if update_method == 'insert':
        # If the datastore already exists, we need to delete it.
        # We can do this through a CKAN API call (if we know
        # the resource ID) or by setting clear_first = True
        # on the pipeline.
        
        # However, the ETL framework fails if you try to 
        # use clear_first = True when the resource doesn't
        # exist, so check that it exists.
        resource_exists = (find_resource_id(site,package_id,kwargs['resource_name'],API_key) is not None)
        if resource_exists:
            clear_first = True

    print("Preparing to pipe data from {} to resource {} package ID {} on {}, using the update method {} with clear_first = {}".format(target,list(kwargs.values())[0],package_id,site,update_method,clear_first))

    super_pipeline = pl.Pipeline('yet_another_pipeline',
                                      'Pipeline for Bitkeeper Data',
                                      log_status=False,
                                      settings_file=SETTINGS_FILE,
                                      settings_from_file=True,
                                      start_from_chunk=0,
                                      chunk_size=chunk_size
                                      ) \
        .connect(pl.FileConnector, target, encoding='utf-8') \
        .extract(pl.CSVExtractor, firstline_headers=True) \
        .schema(schema) \
        .load(pl.CKANDatastoreLoader, server,
              clear_first=clear_first,
              fields=fields,
              #package_id=package_id,
              #resource_id=resource_id,
              #resource_name=resource_name,
              key_fields=primary_keys,
              method=update_method,
              **kwargs).run()
    log = open('uploaded.log', 'w+')
    if specify_resource_by_name:
        message = "Piped data to {}".format(kwargs['resource_name'])
        print(message)
        log.write("Finished upserting {} at {} \n".format(kwargs['resource_name'],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    else:
        message = "Piped data to {}".format(kwargs['resource_id'])
        print(message)
        log.write("Finished upserting {} at {} \n".format(kwargs['resource_id'],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    log.close()
    ntf.close()
    assert not os.path.exists(target)

    resource_id = find_resource_id(site,package_id,kwargs['resource_name'],API_key)
    csv_download_url = get_resource_parameter(site,resource_id,'url',API_key)

    name = get_package_parameter(site,package_id,'name',API_key)

    #resources = get_package_parameter(site,package_id,'resources',API_key)

    #for r in resources:
    #    if r['id'] == resource_id:
    #        resource_url = 
   
    package_url = "{}/dataset/{}".format(site,name)
    return message, package_url, csv_download_url

def schema_by_table(table_name,fields_to_include):
    """This function generates a Marshmallow schema based on the Django app's model fields."""

    # Originally this generation of schemas was including the wrong end of m2m fields,
    # which should not be in the schema. The addition parameter fields_to_include
    # was added for filtering out these other fields.

    # Sample schema:
    #    class ElectionResultsSchema(pl.BaseSchema):
    #        line_number = fields.Integer(dump_to="line_number", allow_none=False)
    #        contest_name = fields.String(allow_none=False)
    #        # NEVER let any of the key fields have None values. It's just asking for
    #        # multiplicity problems on upsert.
    #
    #        # [Note that since this script is taking data from CSV files, there should be no
    #        # columns with None values. It should all be instances like [value], [value],, [value],...
    #        # where the missing value starts as as a zero-length string, which this script
    #        # is then responsible for converting into something more appropriate.
    #
    #        class Meta:
    #            ordered = True

    target_table = getattr(models, table_name) # Fetch the Django model by name
    disordered_model_fields = target_table._meta.get_fields() # This returns the fields 
    # in an order that might be different from the order they're defined in models.py
    # (but it seems to be the same as the order that a previous version of the code
    # created). Basically it's weird things like the ManyToOne relations (Council 
    # Members in Municipality) and the id field that appear in different
    # places (either before or after all the rest of the fields), so this distinction
    # is not important at this point.

    filtered_model_fields = [f for f in disordered_model_fields if f in fields_to_include]

    type_to_field = {'AutoField': fields.Integer,
            'CharField': fields.String,
            'FloatField': fields.Float,
            'SmallIntegerField': fields.Integer,
            'IntegerField': fields.Integer,
            'ForeignKey': fields.String,  # Of course, not all
            # foreign keys are strings, but we're going to coerce
            # them to be so for now.
            'ManyToManyField': fields.String,
            #django_models.SmallIntegerField(): fields.Integer,
            }

    # To dynamically create a class, do this:   type(name, bases, attributes)
    attributes = OrderedDict()
    # Here's an example with a class method:
    #    NewClass = type("NewClass", (object,), {
    #        "string_val": "this is val1",
    #        "int_val": 10,
    #        "__init__": constructor,
    #        "func_val": some_func,
    #        "class_func": some_class_method
    #    }))
    primary_keys = []
    for field in filtered_model_fields:
        if keep(field) and field.get_internal_type() != 'AutoField':
            #for x in dir(field):
            #    if x[0] != '_':
            #        try:
            #            print(x,getattr(field,x))
            #        except:
            #            print("You can't just go and print the {} of {}. It's not that simple!".format(x,field))
            #    print("       internal type for {} in {} = {}".format(field.name,target_table,field.get_internal_type() ))
            django_field_type = field.get_internal_type() # This is a string name for the field type.
            marshmallow_field = type_to_field[django_field_type]
            kwargs = {}
            kwargs['allow_none'] = True
            if hasattr(field,'unique') and field.unique:
                primary_keys.append(field.name)
                kwargs['allow_none'] = False
            elif hasattr(field,'primary_key') and field.primary_key:
                primary_keys.append(field.name)
                kwargs['allow_none'] = False

            attributes[field.name] = marshmallow_field(**kwargs) 

    SchemaClass = type("ThingSchema", (pl.BaseSchema,), attributes)



    unordered_fields_to_publish = SchemaClass().serialize_to_ckan_fields() # This is a list of dicts encoded for CKAN.
    fields_to_publish = []
    for mf in filtered_model_fields:
        for uf in unordered_fields_to_publish:
            if mf.name == uf['id']:
                fields_to_publish.append(uf)

    assert(len(fields_to_publish) == len(fields_to_include))
    # [ ] Since this assertion has not been violated yet, it seems quite likely that
    # fields_to_publish is identical to fields_to_include and that the former
    # could be eliminated here.


    return SchemaClass, fields_to_publish, primary_keys

def serialized_value(xs):
    if len(xs) == 0:
        return None
    if len(xs) == 1:
        return xs[0]
    return '|'.join([str(x) for x in xs])

def export_table_to_ckan(request,table_name):
    if not request.user.is_authenticated():
        return redirect('%s?next=%s' % ('/admin/login/', request.path))

    try:
        target_table = getattr(models, table_name)
    except AttributeError:
        target_table = None
        print("Send back a message that that table could not be found.")

    from django.core import serializers
    data = json.loads(serializers.serialize("json", target_table.objects.all()))
    #pprint(data)

    # data looks like this:
    # [{'fields': {'address_city': 'Pittsburgh',
    #         'contact': '412.237.1890',
    #         'library_name': 'Allegheny',
    #         'street_address': '1230 Federal Street',
    #         'web_site': 'http://www.carnegielibrary.org',
    #         'zip_code': '15212'},
    #  'model': 'bitkeeper.library',
    #  'pk': 46},
    # {'fields': {'address_city': 'Pittsburgh', [...]
    raw_list_of_dicts = [d['fields'] for d in data]
    # This initial list of dicts has just indices for 
    # foreign-key fields and lists of indices for 
    # many-to-many fields. It's necessary to convert those
    # into values to make the exported data more human-readable.
    model_fields = target_table._meta.get_fields()
    model_field_by_name = {f.name:f for f in model_fields}

    list_of_dicts = []
    fields_to_publish = []
    for d in raw_list_of_dicts:
        baked_d = dict(d)
        for k,v in d.items():
            # If the k field is a foreign key or a many-to-many field
            # take v as an index and look up the value or values in
            # the referenced model.
            model_field = model_field_by_name[k]
            if model_field not in fields_to_publish:
                fields_to_publish.append(model_field)
            if model_field.get_internal_type() in ['ForeignKey','ManyToManyField']:
                if model_field.get_internal_type() == 'ManyToManyField' and model_field.many_to_many and model_field.remote_field.get_internal_type() == 'ManyToManyField': # This
                    # if clause is long because I was trying to filter out the other end of the Municipality-StateSentateDistrict.district many-to-many field
                    # but it turns out that it's not in the data exported by the JSON serializer. It's sneaking in through the schema_by_table function...
                    list_of_indices = v
                elif model_field.get_internal_type() == 'ForeignKey':
                    list_of_indices = [v]

                actual_values = [] 
                if list_of_indices not in [None, [], [None]]:
                    for index in list_of_indices:
                        related_row = model_field.related_model.objects.get(pk=index)
                        actual_values.append(str(related_row))

                baked_d[k] = serialized_value(actual_values)
        list_of_dicts.append(baked_d)

    # This is a field (from State Senate District) that we want to not export to CKAN
    #municipality, many_to_many = True, many_to_one = False, one_to_many = False, get_internal_type = ManyToManyField
    #      f.remote_field = bitkeeper.Municipality.state_senate_district

    # But here's what it looks like in Municipality:
    #state_senate_district, many_to_many = True, many_to_one = False, one_to_many = False, get_internal_type = ManyToManyField
    #      f.remote_field = <ManyToManyRel: bitkeeper.municipality> ==> type = ManyToManyField
    #      f.related_model = <class 'bitkeeper.models.StateSenateDistrict'>

    # The distinguishing characteristic is what the remote_field field looks like.

    # One that is still getting through that we would like to suppress:
    # municipality, many_to_many = True, many_to_one = False, one_to_many = False, get_internal_type = ManyToManyField
    #  f.remote_field = bitkeeper.Municipality.fire_department ==> type = ManyToManyField
    #  f.related_model = <class 'bitkeeper.models.Municipality'>

    schema, ckan_fields, primary_keys = schema_by_table(table_name,fields_to_publish)

    resource_name_base = target_table._meta.verbose_name_plural
    resource_name_base = resource_name_base[0].upper() + resource_name_base[1:]
    result, package_url, csv_download__url = send_data_to_pipeline(resource_name_base,table_name,schema,list_of_dicts,ckan_fields,primary_keys,chunk_size=5000)


    context = {'result': result, 'message': 'The data portal page for this datset is <a href="{}">{}</a>'.format(package_url,package_url)}
    # [ ] At present, this will just break if the data fails to upsert.
    return render(request, 'bitkeeper/results.html', context)

def keep(field):
    if field.get_internal_type() == 'ForeignKey':
        return not field.one_to_many
    return True

def csv_view(request,table_name):
    if not request.user.is_authenticated():
        return redirect('%s?next=%s' % ('/admin/login/', request.path))
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(table_name)

    writer = csv.writer(response)
    target_table = getattr(models, table_name)

    model_fields = [f for f in target_table._meta.get_fields()]
    field_names = [f.name for f in target_table._meta.get_fields() if keep(f)]

    warning_issued = []
    for i,obj in enumerate(target_table.objects.all()):
        row = []
        for field in model_fields:
            if keep(field):
                if field.get_internal_type() == 'ManyToManyField' and field.many_to_many:
                    try:
                        qset = getattr(obj, field.name).all() # This is a queryset
                        row.append(', '.join([str(q) for q in qset]))
                    except AttributeError:
                        print(field.related_model())
                        if field.name not in warning_issued:
                            print("Unable to find the field {} in {} object".format(field.name, target_table))
                            warning_issued.append(field.name)
                else:
                    row.append(getattr(obj, field.name))
        if i == 0:
            field_names_to_output = [n for n in field_names if n not in warning_issued]
            writer.writerow(field_names_to_output) # Write CSV file header
        writer.writerow(row)

    return response

def index(request):
    if not request.user.is_authenticated():
        return redirect('%s?next=%s' % ('/admin/login/', request.path))
        #return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    app_name = 'bitkeeper1'
    from django.apps import apps
    from django.contrib import admin
    from django.contrib.admin.sites import AlreadyRegistered

    all_models = apps.get_app_config(app_name).get_models()

    table_names = []
    table_stats = []
    na_rows = []
    na_models = []

    keys_added = []

    for model in all_models:
        table_names.append(model.__name__) #model._meta.object_name)
        all_objects = model.objects.all()
        table_stats.append({'table_name': model.__name__, 'row_count': len(all_objects)})
        for field in model._meta.get_fields():
            if field.name not in ['id']:
                field_type_name = field.get_internal_type()
                if field_type_name in ['SmallIntegerField', 'IntegerField', 'FloatField', 'DecimalField']:
                    search_kwargs = {field.name: 0}
                else:
                    search_kwargs = {field.name: 'N/A'}
                if field_type_name not in ['ForeignKey', 'ManyToManyField']:
                    for row in model.objects.filter(**search_kwargs):
                        key = "{}|{}".format(model.__name__,row.pk)
                        if key not in keys_added:
                            na_rows.append(row)
                            na_models.append(model.__name__)
                            keys_added.append(key)

    nas = zip(na_rows, na_models)
    context = {'table_stats': table_stats, 'table_names': table_names,
            'nas': nas, 'len_of_nas': len(na_rows) }
    return render(request, 'bitkeeper1/index.html', context)
    #template = loader.get_template('index.html')

    #return HttpResponse(template.render(context, request))

# Actually just use the simpleisbetterthancomplex.com 
# examples after pip-installing django-import-export.

# The following should serve an admin-only page
#@user_passes_test(lambda u: u.is_staff)
#def UploadFileView(request, *args, **kwargs):
#
## import CSV file
#    for line in csv_file:
#        # Parse line into fields
#        # Build row out of fields
#        fd = fire_department(name = ,
#            street_address = ,
#    
#    return render_to_response("admin/base_form.html", {'form_text': form_text},context_instance=RequestContext(request))
