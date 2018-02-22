# bitkeeper

## Installation Tips

Do this:

```
>>>  pip install django-csvimport
```

Modify the settings.py file of your Django project to include these INSTALLED APPS:

```python
INSTALLED_APPS = [
     .
     .
     .
    'bitkeeper',
    'csvimport.app.CSVImportConf'  # use AppConfig for django >=1.7 csvimport >=2.2
]
```

Then do this:

```
python manage.py migrate
```
