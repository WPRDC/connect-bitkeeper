from django.db import models

class FireDepartment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

class PoliceDepartment(models.Model):
    police_station = models.CharField(max_length=100, unique=True)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    chief_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    chief_email = models.CharField(max_length=90, blank=True, null=True, editable=True)
    web_site = models.CharField(max_length=90, blank=True, null=True)

class EMSDepartment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    director_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    director_email = models.CharField(max_length=100, blank=True, null=True)
    web_site = models.CharField(max_length=90, blank=True, null=True)

class Municipality(models.Model):
    municipality = models.CharField(max_length=100, unique=True)
    cog = models.CharField(verbose_name = "COG", max_length=100)
    congressional_district = models.SmallIntegerField()
    municipal_web_site = models.CharField(max_length=100, blank=True, null=True)
    mayor = models.CharField(max_length=100, blank=True, null=True)
    manager_or_secretary = models.CharField(max_length=100, blank=True, null=True)
    manager_contact = models.CharField(max_length=200, blank=True, null=True)
    school_district = models.CharField(max_length=100, blank=True, null=True)
    # [ ] School district could also be a separate table.
    

    ems_department = models.ForeignKey(EMSDepartment,null=True)
    # Each CouncilMember maps to one Municipality, but 
    # each Municipality has multiple CouncilMembers.
    # Similarly, each Municipality maps to one EMS/Fire/Police Department,
    # but some of those Departments can map to multiple Municipalities.

    fire_department = models.ForeignKey(FireDepartment,null=True)
    
    # [ ] state_house_representative, state_house_representative_party, state_senator, and state_senator_party need to be linked other tables through the district numbers

    class Meta:
        verbose_name_plural = "municipalities"

class CouncilMember(models.Model):
    name = models.CharField(max_length=100)
    municipality = models.ForeignKey(Municipality)

class StateHouseDistrict(models.Model):
    district = models.SmallIntegerField()
    municipality = models.ForeignKey(Municipality)

class StateSenateDistrict(models.Model):
    district = models.SmallIntegerField()
    municipality = models.ForeignKey(Municipality)

