from django.db import models


class FireDepartment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    street_address = models.CharField(max_length=100)
    address_city = models.CharField(max_length=50) # The mailing address
    # may often have a city value of "Pittsburgh" even though the 
    # location is in some other municipality, so we use the disambiguating
    # field name "address_city".
    zip_code = models.CharField(max_length=10)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = "fire department"

    def __str__(self):
        return '{}'.format(self.name)

class PGHCouncilDistrict(models.Model):
    council_district = models.SmallIntegerField(unique=True)
    committee = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, blank=True, null=True)
    council_member = models.CharField(max_length=100) # This is city council
    # members, and there's only one for each Pittsburgh city council
    # district, so this is a one-to-one relationship.

    # Departments are all linked to PGH council districts
    # with foreign-key relationships in such a way that 
    # multiple police/EMS departments can be in the same
    # Pittsburgh council district.

    class Meta:
        verbose_name = "Pittsburgh council district"
        verbose_name_plural = "Pittsburgh council districts"

    def __str__(self):
        return '{}'.format(self.council_district)

class EMSDepartment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    street_address = models.CharField(max_length=100)
    address_city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    director_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    director_email = models.CharField(max_length=100, blank=True, null=True)
    web_site = models.CharField(max_length=90, blank=True, null=True)
    pittsburgh_council_district = models.ForeignKey(PGHCouncilDistrict, blank=True, null=True)

    class Meta:
        verbose_name = "EMS department"

    def __str__(self):
        return '{}'.format(self.name)

class PoliceDepartment(models.Model):
    police_station = models.CharField(max_length=100, unique=True)
    street_address = models.CharField(max_length=100)
    address_city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    chief_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    chief_email = models.CharField(max_length=90, blank=True, null=True)
    web_site = models.CharField(max_length=90, blank=True, null=True)
    pittsburgh_council_district = models.ForeignKey(PGHCouncilDistrict, blank=True, null=True)

    class Meta:
        verbose_name = "police department"

    def __str__(self):
        return '{}'.format(self.police_station)


class Watershed(models.Model):
    watershed_name = models.CharField(max_length=100, unique=True)
    watershed_association = models.CharField(max_length=100,blank=True,null=True)

    # [ ] Is it correct that there's one watershed association associated
    # with each watershed? Can there be zero?

    class Meta:
        verbose_name = "watershed"

    def __str__(self):
        return self.watershed_name

class StateSenateDistrict(models.Model):
    district = models.SmallIntegerField(unique=True)
    senator_first_name = models.CharField(max_length=50, blank=True, null=True)
    senator_last_name = models.CharField(max_length=50, blank=True, null=True)
    senator_suffix = models.CharField(max_length=20, blank=True, null=True)
    senator_home_county = models.CharField(max_length=30, blank=True, null=True)
    senator_party = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name = "state Senate district"

    def __str__(self):
        return '{}'.format(self.district)

class StateHouseDistrict(models.Model):
    district = models.SmallIntegerField(unique=True)
    rep_first_name = models.CharField(max_length=50, blank=True, null=True)
    rep_last_name = models.CharField(max_length=50, blank=True, null=True)
    rep_suffix = models.CharField(max_length=20, blank=True, null=True)
    rep_home_county = models.CharField(max_length=30, blank=True, null=True)
    rep_party = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name = "state House district"

    def __str__(self):
        return '{}'.format(self.district)

class Municipality(models.Model):
    municipality = models.CharField(max_length=100, unique=True)
    municode = models.IntegerField(blank=True, null=True) # These are actually unique, so they could be used as primary keys,
    # but doing so would interfere with the data export process.

    # I obtained these municode values from the Allegheny County Municipal Boundaries dataset:
    # https://data.wprdc.org/dataset/allegheny-county-municipal-boundaries/resource/e688bfa3-e005-4b3c-894c-6ed21a5d0227
    cog = models.CharField(verbose_name = "COG", max_length=100, blank=True, null=True)
    congressional_district = models.SmallIntegerField(blank=True, null=True)
    municipal_web_site = models.CharField(max_length=100, blank=True, null=True)
    mayor = models.CharField(max_length=100, blank=True, null=True)
    manager_or_secretary = models.CharField(max_length=100, blank=True, null=True)
    manager_contact = models.CharField(max_length=200, blank=True, null=True)
    school_district = models.CharField(max_length=100, blank=True, null=True)
    # [ ] School district could also be a separate table.
    state_house_district = models.ManyToManyField(StateHouseDistrict,verbose_name="state House district",blank=True)
    state_senate_district = models.ManyToManyField(StateSenateDistrict,verbose_name="state Senate district",blank=True)
    county_council_district = models.SmallIntegerField(blank=True, null=True)
    # [ ] state_house_representative, state_house_representative_party, state_senator, and state_senator_party need to be linked to other tables through the district numbers.
    municipal_address = models.CharField(max_length=100, blank=True, null=True)
    municipal_city = models.CharField(max_length=50, blank=True, null=True)
    municipal_zip_code = models.CharField('municipal ZIP code', max_length=10, blank=True, null=True)

    ems_department = models.ForeignKey(EMSDepartment,verbose_name="EMS department",null=True,blank=True)
    police_department = models.ForeignKey(PoliceDepartment,null=True,blank=True)
    # Each CouncilMember maps to one Municipality, but 
    # each Municipality has multiple CouncilMembers.
    # Similarly, each Municipality maps to one EMS/Police Department,
    # but some of those Departments can map to multiple Municipalities.

    fire_department = models.ManyToManyField(FireDepartment,blank=True)
    # Two municipalities have multiple fire departments, making this and two fire departments
    # map to multiple municipalities, making this a many-to-many field.

    # watershed is a many-to-many relationship, since each municipality
    # can belong to multiple watersheds and each watershed can be in 
    # multiple municipalities.
    watershed = models.ManyToManyField(Watershed,blank=True)

    class Meta:
        verbose_name_plural = "municipality"
        verbose_name_plural = "municipalities"

    def __str__(self):
        return '{}'.format(self.municipality)

class CouncilMember(models.Model):
    name = models.CharField(max_length=100)
    municipality = models.ForeignKey(Municipality)

    class Meta:
        verbose_name = "council member"

    def __str__(self):
        return self.name

class Library(models.Model):
    library_name = models.CharField(max_length=100,unique=True)
    street_address = models.CharField(max_length=100)
    address_city = models.CharField(max_length=50)
    #state = models.CharField(max_length=2)
    # Why is the state listed here but not elsewhere?
    # I think it's fine to just assume that the state is "PA" 
    # everywhere in this database until that becomes untrue.
    zip_code = models.CharField(max_length=10)
    web_site = models.CharField(max_length=90, blank=True, null=True)
    contact = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "library"
        verbose_name_plural = "libraries"

    def __str__(self):
        return 'Library: {}'.format(self.library_name)

