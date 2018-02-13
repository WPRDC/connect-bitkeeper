from django.db import models

class Municipality(models.Model):
    municipality = models.CharField(max_length=100, unique=True, editable=True)
    cog	= models.CharField(max_length=100, editable=True)
    congressional_district = models.SmallIntegerField(editable=True)
    municipal_web_site = models.CharField(max_length=100, blank=True, null=True, editable=True)

class CouncilMember(models.Model):
    name = models.CharField(max_length=100, editable=True)
    municipality = models.ForeignKey(Municipality)

class FireDepartment(models.Model):
    name = models.CharField(max_length=100, unique=True, editable=True)
    street_address = models.CharField(max_length=100, editable=True)
    city = models.CharField(max_length=50, editable=True)
    zip_code = models.CharField(max_length=10, editable=True)
    latitude = models.FloatField(blank=True, null=True, editable=True)
    longitude = models.FloatField(blank=True, null=True, editable=True)

class PoliceDepartment(models.Model):
    police_station = models.CharField(max_length=100, unique=True, editable=True)
    street_address = models.CharField(max_length=100, editable=True)
    city = models.CharField(max_length=50, editable=True)
    zip_code = models.CharField(max_length=10, editable=True)
    chief_name = models.CharField(max_length=50, blank=True, null=True, editable=True)
    phone = models.CharField(max_length=50, blank=True, null=True, editable=True)
    chief_email = models.CharField(max_length=90, blank=True, null=True, editable=True)
    web_site = models.CharField(max_length=90, blank=True, null=True, editable=True)

