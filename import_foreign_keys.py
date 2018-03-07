# This script can be run from the Django shell like this:
#   $ ./manage.py shell
#   >>> exec(open('bitkeeper/import_foreign_keys.py').read())
import csv

from bitkeeper.models import Municipality,EMSDepartment,FireDepartment,PoliceDepartment

def link_foreign_key(foreign_key_string,model,model_field,target_object,target_field):
    foreign_keys = foreign_key_string.split(', ')
    for foreign_key in foreign_keys:
        try:
            kwargs = {model_field: foreign_key}
            item = model.objects.get(**kwargs)
            if item is not None:
                #target_object.ems_department = item
                setattr(target_object, target_field, item)
                target_object.save()
        except: #DoesNotExist:
            print(" *** Unable to find {} in {}. ***".format(foreign_key, model))

with open('bitkeeper/data/municipality.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # The header row values become your keys
        #suite_name = row['SuiteName']
        #test_case = row['Test Case']
        # etc....
        print(row['municipality'])
        municipality = Municipality.objects.get(municipality=row['municipality'])
        #print(row['ems_department'])
        link_foreign_key(row['ems_department'],EMSDepartment,'name',municipality,'ems_department')
        link_foreign_key(row['fire_department'],FireDepartment,'name',municipality,'fire_department')
        link_foreign_key(row['police_station'],PoliceDepartment,'police_station',municipality,'police_department')
        #try:
        #    ems = EMSDepartment.objects.get(name=row['ems_department'])
        #    if ems is not None:
        #        municipality.ems_department = ems
        #        municipality.save()
        #except: #DoesNotExist:
        #    print(" *** Unable to find {} in EMSDepartment. ***".format(row['ems_department']))


