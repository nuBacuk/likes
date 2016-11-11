from django.conf.urls import url
from .likes import *

urlpatterns = [
	url(r'^like', uri_manager, name='likes'),
	url(r'^auth', authorize, name='auth'),
]
