from django.shortcuts import render

#from django.contrib.auth.decorators import user_passes_test
#from django.shortcuts import render_to_response

from .models import FireDepartment, PoliceDepartment
#from django.template import loader
#from django.http import HttpResponse

def index(request):
    app_name = 'bitkeeper'
    from django.apps import apps
    from django.contrib import admin
    from django.contrib.admin.sites import AlreadyRegistered

    all_models = apps.get_app_config(app_name).get_models()

    table_names = []
    tables = [] 
    table_stats = []
    for model in all_models:
        table_names.append(model._meta.db_table)
        all_objects = model.objects.all()
        tables.append(all_objects)
        table_stats.append([model._meta.db_table, len(all_objects)])
        print(dir(model))

    print(table_stats)
    fds = FireDepartment.objects.order_by('name')
    context = {'fire_departments': fds, 'table_stats': table_stats, 'tables': tables}
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
