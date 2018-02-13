from django.contrib import admin

from .models import Municipality, FireDepartment, PoliceDepartment

class FireDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'street_address', 'city', 'zip_code']

    search_fields = list_display
    ordering = ['name']

admin.site.register(FireDepartment, FireDepartmentAdmin)

class PoliceDepartmentAdmin(admin.ModelAdmin):
    list_display = ['police_station', 'street_address', 'city', 'zip_code', 'chief_name', 'phone', 'chief_email']

    search_fields = list_display
    ordering = ['police_station']

admin.site.register(PoliceDepartment, PoliceDepartmentAdmin)
