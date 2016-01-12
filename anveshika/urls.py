"""anveshika URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns,include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'anveshikaapp.views.home', name='anveshikaapp.home'),
	url(r'^register$', 'anveshikaapp.views.register', name='register'),
	url(r'^login$', 'anveshikaapp.views.login_user', name='login'),
    url(r'^logout$', 'anveshikaapp.views.logout_user', name='logout'),
	url(r'^upload/$', 'anveshikaapp.views.upload', name='imageupload'),
	url(r'^listpositions/$', 'anveshikaapp.views.listpositions', name='listpositions'),
	url(r'^viewsamples/$', 'anveshikaapp.views.viewsamples', name='viewsamples'),
	url(r'^viewannotations/$', 'anveshikaapp.views.viewannotations', name='viewannotations'),
	url(r'^viewsampledata/$', 'anveshikaapp.views.viewsampledata', name='viewsampledata'),
	url(r'^viewannotationdata/$', 'anveshikaapp.views.viewannotationdata', name='viewannotationdata'),
	url(r'^listtsttable/$', 'anveshikaapp.views.listtsttable', name='listtsttable'),
	url(r'^search/$', 'anveshikaapp.views.search', name='search'),
	url(r'^searchresult/$', 'anveshikaapp.views.searchresult', name='searchresult'),
	url(r'^possearch/$', 'anveshikaapp.views.posSearch', name='posSearch'),
	url(r'^possearchresult/$', 'anveshikaapp.views.possearchresult', name='possearchresult'),
	url(r'^psesearch/$', 'anveshikaapp.views.pseSearch', name='pseSearch'),
	url(r'^psesearchresult/$', 'anveshikaapp.views.psesearchresult', name='psesearchresult'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
