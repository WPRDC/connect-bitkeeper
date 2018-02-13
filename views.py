from django.shortcuts import render

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response

from .models import FireDepartment, PoliceDepartment


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
