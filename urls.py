from django.conf.urls import url

from . import views

urlpatterns = [
#    url(r'^$', views.index, name='index'),
    url(r'^$', views.index, name='index'), #/bitkeeper goes here.
    url(r'^(?P<table_name>[^/]+)/csv$', views.csv_view, name='show_csv'),
    #url(r'data$', views.data, name='data'),
    #    url(r'^(?P<resource_id>[^/]+)/(?P<field>.*)/(?P<search_term>.*)$', views.results, name='results'),
    ]
