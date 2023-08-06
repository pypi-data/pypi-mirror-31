"""piton URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
pitons:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
#from django.conf.urls import url
from django.urls import path
#from .brython import Brython
from . import views

urlpatterns = [

    path('open_url/', views.open_url.as_view(), name='radiant-open_url'),
    path('logs/', views.logs.as_view(), name='radiant-logs'),
    path('mdc-theme.css/', views.theme.as_view(), name='mdc-theme.css'),

    #url(r'^brython/$', Brython.as_view(), name='brython'),


]