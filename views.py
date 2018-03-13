from django.shortcuts import render

#from django.contrib.auth.decorators import user_passes_test
#from django.shortcuts import render_to_response

from .models import FireDepartment, PoliceDepartment
#from django.template import loader
from django.http import HttpResponse
import csv
from bitkeeper import models
from marshmallow import fields, pre_load, post_load
sys.path.insert(0, '/Users/drw/WPRDC/etl-dev/wprdc-etl') # A path that we need to import code from
import pipeline as pl

class SchemaAtom(pl.BaseSchema):
    class Meta:
        ordered = True

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
    model_fields = target_table._meta.get_fields()

    # The fields will probably need to be pared down in a way similar to
    # that used for generating the CSV fields, so some refactoring is in order.

    #   [ ] Refactor!

    type_to_field = {'AutoField': fields.Integer,
            'CharField': fields.String,
            'SmallIntegerField': fields.Integer,
            'ForeignKey': fields.String,  # Of course, not all
            # foreign keys are strings, but we're going to coerce
            # them to be so for now.
            'ManyToManyField': fields.String,
            #django_models.SmallIntegerField(): fields.Integer,
            }

    # To dynamically create a class, do this:   type(name, bases, attributes)
    attributes = {}
    # Here's an example with a class method:
    #    NewClass = type("NewClass", (object,), {
    #        "string_val": "this is val1",
    #        "int_val": 10,
    #        "__init__": constructor,
    #        "func_val": some_func,
    #        "class_func": some_class_method
    #    }))
    primary_keys = []
    for field in model_fields:
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
            if field.unique or field.primary_key:
                primary_keys.append(field.name)
                kwargs['allow_none'] = False
            attributes[field.name] = marshmallow_field(**kwargs) #fields.something(with parameters determined and set here)

    pprint(attributes)
    SchemaClass = type("ThingSchema", (pl.BaseSchema,), attributes)

    fields_to_publish = SchemaClass().serialize_to_ckan_fields()
    pprint(fields_to_publish)
    return SchemaClass, fields_to_publish, primary_keys

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
    for model in all_models:
        table_names.append(model.__name__) #model._meta.object_name)
        all_objects = model.objects.all()
        table_stats.append([model.__name__, len(all_objects)])

    print(table_stats)
    context = {'table_stats': table_stats, 'table_names': table_names}
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
