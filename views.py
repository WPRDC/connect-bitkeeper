from django.shortcuts import render

#from django.contrib.auth.decorators import user_passes_test
#from django.shortcuts import render_to_response

from .models import FireDepartment, PoliceDepartment
#from django.template import loader
from django.http import HttpResponse
import csv
from bitkeeper import models

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
    fields = [f for f in target_table._meta.get_fields()]
    print(fields)
    print(dir(fields[0]))
    for f in fields:
        print("{}, many_to_many = {}, many_to_one = {}, one_to_many = {}, get_internal_type = {}".format(f.name, f.many_to_many, f.one_to_one, f.one_to_many, f.get_internal_type()))
        try:
            print("      f.remote_field = {}".format(f.remote_field))
        except:
            pass
    field_names = [f.name for f in target_table._meta.get_fields() if keep(f)]
    print(field_names)
    writer.writerow(field_names) # Write CSV file header
    for obj in target_table.objects.all():
        row = []
        for field in fields:
            if keep(field):
                if field.get_internal_type() == 'ManyToManyField' and field.many_to_many:
                    qset = getattr(obj, field.name).all() # This is a queryset
                    row.append(', '.join([str(q) for q in qset]))
                else:
                    row.append(getattr(obj, field.name))
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
