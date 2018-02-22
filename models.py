from django.db import models

class FireDepartment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return 'Fire Department: {}'.format(self.name)

class PoliceDepartment(models.Model):
    police_station = models.CharField(max_length=100, unique=True)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    chief_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    chief_email = models.CharField(max_length=90, blank=True, null=True, editable=True)
    web_site = models.CharField(max_length=90, blank=True, null=True)

    def __str__(self):
        return 'Police Department: {}'.format(self.police_station)

class EMSDepartment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    director_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    director_email = models.CharField(max_length=100, blank=True, null=True)
    web_site = models.CharField(max_length=90, blank=True, null=True)

    class Meta:
        verbose_name = "EMS department"

    def __str__(self):
        return 'EMS Department: {}'.format(self.name)

class PGHCouncilDistrict(models.Model):
    council_district = models.SmallIntegerField(unique=True,primary_key=True)
    committee = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, blank=True, null=True)
    council_member = models.CharField(max_length=100) # This is city council
    # members, and there's only one for each Pittsburgh city council
    # district, so this is a one-to-one relationship.

    # Departments are all linked to PGH council districts
    # with foreign-key relationships.
    ems_department = models.ForeignKey(EMSDepartment,verbose_name="EMS department",null=True,blank=True)
    police_department = models.ForeignKey(PoliceDepartment,null=True,blank=True)

    def __str__(self):
        return 'PGH Council District {}'.format(self.council_district)

    class Meta:
        verbose_name = "PGH council district"
        verbose_name_plural = "PGH council districts"

class Watershed(models.Model):
    watershed_name = models.CharField(max_length=100)
    watershed_association = models.CharField(max_length=100,blank=True,null=True)

    # [ ] Is it correct that there's one watershed association associated
    # with each watershed? Can there be zero?

    def __str__(self):
        return self.watershed_name


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
    state_house_district =  models.SmallIntegerField(blank=True, null=True)
    state_senate_district =  models.SmallIntegerField(blank=True, null=True)
    county_council_district =  models.SmallIntegerField(blank=True, null=True)
    # [ ] state_house_representative, state_house_representative_party, state_senator, and state_senator_party need to be linked to other tables through the district numbers.
    municipal_address = models.CharField(max_length=100, blank=True, null=True)
    municipal_city= models.CharField(max_length=50, blank=True, null=True)
    municipal_zip_code = models.CharField(max_length=10, blank=True, null=True)

    ems_department = models.ForeignKey(EMSDepartment,verbose_name="EMS department",null=True,blank=True)
    # Each CouncilMember maps to one Municipality, but 
    # each Municipality has multiple CouncilMembers.
    # Similarly, each Municipality maps to one EMS/Fire/Police Department,
    # but some of those Departments can map to multiple Municipalities.

    fire_department = models.ForeignKey(FireDepartment,null=True,blank=True)
    police_department = models.ForeignKey(PoliceDepartment,null=True,blank=True)

    # watershed is a many-to-many relationship, since each municipality
    # can belong to multiple watersheds and each watershed can be in 
    # multiple municipalities.
    watershed = models.ManyToManyField(Watershed,null=True,blank=True)

    class Meta:
        verbose_name_plural = "municipalities"

    def __str__(self):
        return 'Municipality: {}'.format(self.municipality)

class CouncilMember(models.Model):
    name = models.CharField(max_length=100)
    municipality = models.ForeignKey(Municipality)

    def __str__(self):
        return self.name

class StateHouseDistrict(models.Model):
    district = models.SmallIntegerField()
    municipality = models.ForeignKey(Municipality)

    def __str__(self):
        return '{}'.format(self.district)

class StateSenateDistrict(models.Model):
    district = models.SmallIntegerField()
    municipality = models.ForeignKey(Municipality)

    def __str__(self):
        return '{}'.format(self.district)

class Library(models.Model):
    library_name = models.CharField(max_length=100,unique=True)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    #state = models.CharField(max_length=2)
    # Why is the state listed here but not elsewhere?
    # I think it's fine to just assume that the state is "PA" 
    # everywhere in this database until that becomes untrue.
    zip_code = models.CharField(max_length=10)
    web_site = models.CharField(max_length=90, blank=True, null=True)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return 'Library: {}'.format(self.library_name)

    class Meta:
        verbose_name_plural = "libraries"
