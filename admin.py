from django.contrib import admin

from .models import Municipality, CouncilMember, FireDepartment, PoliceDepartment, Library

class CouncilMemberInline(admin.TabularInline):
    model = CouncilMember

class MunicipalityAdmin(admin.ModelAdmin):
    inlines = [CouncilMemberInline]
    list_display = ['municipality', 'cog', 'congressional_district','municipal_web_site']

    search_fields = list_display
    ordering = ['municipality']

admin.site.register(Municipality, MunicipalityAdmin)

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




class LibraryAdmin(admin.ModelAdmin):
    list_display = ['library_name', 'street_address', 'city', 'zip_code', 'web_site', 'contact']

    search_fields = list_display
    ordering = ['library_name']

admin.site.register(Library, LibraryAdmin)
