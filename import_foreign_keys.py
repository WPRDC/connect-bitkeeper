# This script can be run from the Django shell like this:
#   $ ./manage.py shell
#   >>> exec(open('bitkeeper/import_foreign_keys.py').read())
import csv

from bitkeeper.models import Municipality,EMSDepartment,FireDepartment,PoliceDepartment,StateSenateDistrict,StateHouseDistrict

def string_to_list(s):
    return s.split(', ')

#How do you save things to a ManyToManyField?
#
#Use the add method for related fields:
#
## using Model.object.create is a shortcut to instantiating, then calling save()
    #myMoveInfo = Movie_Info.objects.create(title='foo', overview='bar')
    #myMovieGenre = Movie_Info_genre.objects.create(genre='horror')
    #myMovieInfo.genres.add(myMoveGenre)
#Unlike modifying other fields, both models must exist in the database prior to doing this, so you must call save before adding the many-to-many relationship. Since add immediately affects the database, you do not need to save afterwards.

# This should also work for foreign keys.

def link_things(list_of_things,model,model_field,target_object,target_field):
    for thing in list_of_things:
        try:
            kwargs = {model_field: thing}
            item = model.objects.get(**kwargs)
            if item is not None:
                #target_object.ems_department = item
                #setattr(target_object, target_field, item)
                #target_object.save()
                getattr(target_object,target_field).add(item)
        except: #DoesNotExist:
            print(" *** Unable to find {} in {}. ***".format(thing, model))

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
    ##fds_by_muni = defaultdict(list) # Idea for accumulating ManyToMany relations in a narrow format; this
    ## is not needed yet since municipality.csv uses ", " delimited lists in single cells at present for
    ## some things (as a workaround). 
    for row in reader:
        # The header row values become your keys
        #suite_name = row['SuiteName']
        #test_case = row['Test Case']
        # etc....
        print(row['municipality'])
        municipality = Municipality.objects.get(municipality=row['municipality'])
        #print(row['ems_department'])
        link_things(string_to_list(row['state_senate_district']),StateSenateDistrict,'district',municipality,'state_senate_district')
        link_things(string_to_list(row['state_house_district']),StateHouseDistrict,'district',municipality,'state_house_district')
        #link_things(string_to_list(row['ems_department']),EMSDepartment,'name',municipality,'ems_department')
        link_foreign_key(row['ems_department'],EMSDepartment,'name',municipality,'ems_department')
        ##fds_by_muni[municipality].append(row['fire_department'])
        link_things(string_to_list(row['fire_department']),FireDepartment,'name',municipality,'fire_department')
        link_things(string_to_list(row['police_station']),PoliceDepartment,'police_station',municipality,'police_department')
        link_foreign_key(row['police_station'],PoliceDepartment,'police_station',municipality,'police_department')
        #try:
        #    ems = EMSDepartment.objects.get(name=row['ems_department'])
        #    if ems is not None:
        #        municipality.ems_department = ems
        #        municipality.save()
        #except: #DoesNotExist:
        #    print(" *** Unable to find {} in EMSDepartment. ***".format(row['ems_department']))

## Process ManyToManyFields:
##for muni,fd_list in fds_by_muni.items():
##    link_things(fd_list,FireDepartment,'name',municipality,'fire_department')

