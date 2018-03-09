from django.contrib import admin

from .models import Municipality, CouncilMember, FireDepartment, PoliceDepartment, EMSDepartment, Library, PGHCouncilDistrict, Watershed, StateSenateDistrict, StateHouseDistrict


admin.site.site_header = 'CONNECT Map Bitkeeper'
admin.site.site_title = 'CONNECT Map Bitkeeper'
admin.site.index_title = 'Bitkeeper'

class EMSInline(admin.TabularInline):
    model = EMSDepartment

class PoliceInline(admin.TabularInline):
    model = PoliceDepartment

class PGHCouncilDistrictAdmin(admin.ModelAdmin):
    inlines = [EMSInline, PoliceInline]
    list_display = ['council_district', 'committee', 'phone', 'council_member']

    search_fields = list_display
    ordering = ['council_district']

admin.site.register(PGHCouncilDistrict, PGHCouncilDistrictAdmin)

class StateSenateDistrictAdmin(admin.ModelAdmin):
    list_display = ['district', 'senator_first_name', 'senator_last_name', 'senator_party']

    search_fields = list_display
    ordering = ['district']

admin.site.register(StateSenateDistrict, StateSenateDistrictAdmin)

class StateHouseDistrictAdmin(admin.ModelAdmin):
    list_display = ['district', 'rep_first_name', 'rep_last_name', 'rep_party']

    search_fields = list_display
    ordering = ['district']

admin.site.register(StateHouseDistrict, StateHouseDistrictAdmin)

class CouncilMemberInline(admin.TabularInline):
    model = CouncilMember

class MunicipalityAdmin(admin.ModelAdmin):
    inlines = [CouncilMemberInline]
    fields = ['municipality', 'state_senate_district','state_house_district','fire_department','ems_department','police_department','watershed']
    list_display = ['municipality','state_sen_district','state_rep_district','fire_dept','ems_department','police_department','watersheds']

    def state_sen_district(self, obj):
        return ", ".join([str(d.district) for d in obj.state_senate_district.all()])
    def state_rep_district(self, obj):
        return ", ".join([str(d.district) for d in obj.state_house_district.all()])
    def fire_dept(self, obj):
        return ", ".join([str(fd.name) for fd in obj.fire_department.all()])
    def ems_dept(self, obj):
        return ", ".join([str(ems.name) for ems in obj.ems_department.all()])
    def watersheds(self, obj):
        return ", ".join([str(w.watershed_name) for w in obj.watershed.all()])

    search_fields = fields
    ordering = ['municipality']

admin.site.register(Municipality, MunicipalityAdmin)

class EMSDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'street_address', 'address_city', 'zip_code']

    search_fields = list_display
    ordering = ['name']

admin.site.register(EMSDepartment, EMSDepartmentAdmin)

class FireDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'street_address', 'address_city', 'zip_code']

    search_fields = list_display
    ordering = ['name']

admin.site.register(FireDepartment, FireDepartmentAdmin)

class PoliceDepartmentAdmin(admin.ModelAdmin):
    list_display = ['police_station', 'street_address', 'address_city', 'zip_code', 'chief_name', 'phone', 'chief_email']

    search_fields = list_display
    ordering = ['police_station']

admin.site.register(PoliceDepartment, PoliceDepartmentAdmin)



class LibraryAdmin(admin.ModelAdmin):
    list_display = ['library_name', 'street_address', 'address_city', 'zip_code', 'web_site', 'contact']

    search_fields = list_display
    ordering = ['library_name']

admin.site.register(Library, LibraryAdmin)

class WatershedAdmin(admin.ModelAdmin):
    list_display = ['watershed_name', 'watershed_association']

    search_fields = list_display
    ordering = ['watershed_name']

admin.site.register(Watershed, WatershedAdmin)
