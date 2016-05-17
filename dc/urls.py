from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^nodes/$', views.nodes, name='nodes'),
    url(r'^nodes/add/$', views.add_node, name='add_node'),
    url(r'^nodes/(?P<node_uuid>[^/]+)/$', views.node, name='node'),
    url(r'^nodes/(?P<node_uuid>[^/]+)/register/$', views.register_node, name='register_node'),
]