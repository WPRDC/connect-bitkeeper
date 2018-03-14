from django.shortcuts import render
from django.db import models as django_models
#from django.contrib.auth.decorators import user_passes_test
#from django.shortcuts import render_to_response

from .models import FireDepartment, PoliceDepartment
#from django.template import loader
from django.http import HttpResponse
import os, sys, csv, json, datetime
from bitkeeper import models
from pprint import pprint
from collections import OrderedDict

from bitkeeper.parameters.local_parameters import BITKEEPER_SETTINGS_FILE as SETTINGS_FILE

from marshmallow import fields, pre_load, post_load
sys.path.insert(0, '/Users/drw/WPRDC/etl-dev/wprdc-etl') # A path that we need to import code from
import pipeline as pl

class SchemaAtom(pl.BaseSchema):
    class Meta:
        ordered = True

def write_to_csv(filename,list_of_dicts,keys):
    with open(filename, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, extrasaction='ignore', lineterminator='\n')
        dict_writer.writeheader()
        dict_writer.writerows(list_of_dicts)

def send_data_to_pipeline(resource_name_base,table_name,schema,list_of_dicts,fields,primary_keys,chunk_size=5000):
    # Taken from github.com/WPRDC/stop-in-the-name-of-data.

    specify_resource_by_name = True
    if specify_resource_by_name:
        kwargs = {'resource_name': 'CONNECT Data: {}'.format(resource_name_base)}
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
    server = "secret-cool-data"
    # Code below stolen from prime_ckan/*/open_a_channel() but really from utility_belt/gadgets
    #with open(os.path.dirname(os.path.abspath(__file__))+'/ckan_settings.json') as f: # The path of this file needs to be specified.
    with open(SETTINGS_FILE) as f:
        settings = json.load(f)
    site = settings['loader'][server]['ckan_root_url']
    package_id = settings['loader'][server]['package_id']

    print("Preparing to pipe data from {} to resource {} package ID {} on {}".format(target,list(kwargs.values())[0],package_id,site))
    #time.sleep(1.0)


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
              fields=fields,
              #package_id=package_id,
              #resource_id=resource_id,
              #resource_name=resource_name,
              key_fields=primary_keys,
              method='upsert',
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

    return message

def schema_by_table(table_name):
    print("Generate a Marshmallow schema based on the Model fields")

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
    # in an order different from the order they're defined in models.py.

#                if field.get_internal_type() == 'ManyToManyField' and field.many_to_many:


    # The fields will probably need to be pared down in a way similar to
    # that used for generating the CSV fields, so some refactoring could be done.

    #   [ ] Refactor!

    type_to_field = {'AutoField': fields.Integer,
            'CharField': fields.String,
            'FloatField': fields.Float,
            'SmallIntegerField': fields.Integer,
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
    for field in disordered_model_fields:
        if keep(field) and field.get_internal_type() != 'AutoField':
            #for x in dir(field):
            #    if x[0] != '_':
            #        try:
            #            print(x,getattr(field,x))
            #        except:
            #            print("You can't just go and print the {} of {}. It's not that simple!".format(x,field))
            #    print("       internal type for {} in {} = {}".format(field.name,target_table,field.get_internal_type() ))
            print("       internal type for {} in {} = {}".format(field.name,target_table,field.get_internal_type() ))
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
    for mf in disordered_model_fields:
        for uf in unordered_fields_to_publish:
            if mf.name == uf['id']:
                fields_to_publish.append(uf)

    return SchemaClass, fields_to_publish, primary_keys

def export_table_to_ckan(request,table_name):
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
    list_of_dicts = [d['fields'] for d in data]
    schema, ckan_fields, primary_keys = schema_by_table(table_name)

    pprint(schema)
    pprint(ckan_fields)
    pprint(primary_keys)
    #message = 'Edit code to send data'
    resource_name_base = target_table._meta.verbose_name_plural.title()
    message = send_data_to_pipeline(resource_name_base,table_name,schema,list_of_dicts,ckan_fields,primary_keys,chunk_size=5000)


    context = {'result': '', 'message': message}
    # [ ] At present, this will just break if the data fails to upsert.
    return render(request, 'bitkeeper/results.html', context)

def keep(field):
    if field.get_internal_type() == 'ForeignKey':
        return not field.one_to_many
    return True

def csv_view(request,table_name):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(table_name)

    writer = csv.writer(response)
    target_table = getattr(models, table_name)

    skipped_types = ['ForeignKey']
    model_fields = [f for f in target_table._meta.get_fields()]
    print(model_fields)
    print(dir(model_fields[0]))
    for f in model_fields:
        print("{}, many_to_many = {}, many_to_one = {}, one_to_many = {}, get_internal_type = {}".format(f.name, f.many_to_many, f.one_to_one, f.one_to_many, f.get_internal_type()))
        try:
            print("      f.remote_field = {}".format(f.remote_field))
        except:
            pass
    field_names = [f.name for f in target_table._meta.get_fields() if keep(f)]
    print(field_names)

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
    app_name = 'bitkeeper'
    from django.apps import apps
    from django.contrib import admin
    from django.contrib.admin.sites import AlreadyRegistered

    all_models = apps.get_app_config(app_name).get_models()

    table_names = []
    table_stats = []
    na_rows = []
    na_models = []

    pks_added = []
    for model in all_models:
        table_names.append(model.__name__) #model._meta.object_name)
        all_objects = model.objects.all()
        table_stats.append([model.__name__, len(all_objects)])
        for field in model._meta.get_fields():
            if field.name not in ['id']:
                field_type_name = field.get_internal_type()
                print(field.name,field_type_name)
                if field_type_name in ['SmallIntegerField', 'IntegerField', 'FloatField', 'DecimalField']:
                    search_kwargs = {field.name: 0}
                else:
                    search_kwargs = {field.name: 'N/A'}
                if field_type_name not in ['ForeignKey', 'ManyToManyField']:
                    for row in model.objects.filter(**search_kwargs):
                        if row.pk not in pks_added:
                            na_rows.append(row)
                            na_models.append(model.__name__)
                            pks_added.append(row.pk)

    nas = zip(na_rows, na_models)
    print(table_stats)

    context = {'table_stats': table_stats, 'table_names': table_names,
            'nas': nas }
    return render(request, 'bitkeeper/index.html', context)
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
