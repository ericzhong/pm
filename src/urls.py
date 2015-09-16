"""pm URL Configuration

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
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from project.forms import PasswordResetByEmailForm
from project.views import ProjectList, ProjectDetail, ProjectCreate, ProjectUpdate, ProjectDelete
from project.views import IssueList, IssueDetail, IssueCreate, IssueUpdate, IssueDelete
from project.views import IssueTypeList, IssueTypeDetail, IssueTypeCreate, IssueTypeUpdate, IssueTypeDelete
from project.views import IssueStatusList, IssueStatusDetail, IssueStatusCreate, IssueStatusUpdate, IssueStatusDelete
from project.views import VersionList, VersionDetail, VersionCreate, VersionUpdate, VersionDelete



urlpatterns = [

    url(r'^$', TemplateView.as_view(template_name="index.html"), name='home'),

    # authentication
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}),
    url(r'^password_reset/$', auth_views.password_reset, {'password_reset_form': PasswordResetByEmailForm}),
    url('^', include('django.contrib.auth.urls')),

    # project
    url(r'^projects/$', ProjectList.as_view(), name='project_list'),
    url(r'^project/(?P<pk>\d+)/$', ProjectDetail.as_view(), name='project_detail'),
    url(r'project/add/$', ProjectCreate.as_view(), name='project_add'),
    url(r'project/(?P<pk>\d+)/update/$', ProjectUpdate.as_view(), name='project_update'),
    url(r'project/(?P<pk>\d+)/delete/$', ProjectDelete.as_view(), name='project_delete'),

    # issue
    url(r'^issues/$', IssueList.as_view(), name='issue_list'),
    url(r'^issue/(?P<pk>\d+)/$', IssueDetail.as_view(), name='issue_detail'),
    url(r'issue/add/$', IssueCreate.as_view(), name='issue_add'),
    url(r'issue/(?P<pk>\d+)/update/$', IssueUpdate.as_view(), name='issue_update'),
    url(r'issue/(?P<pk>\d+)/delete/$', IssueDelete.as_view(), name='issue_delete'),

    # issue type
    url(r'^issue_types/$', IssueTypeList.as_view(), name='issue_type_list'),
    url(r'^issue_type/(?P<pk>\d+)/$', IssueTypeDetail.as_view(), name='issue_type_detail'),
    url(r'issue_type/add/$', IssueTypeCreate.as_view(), name='issue_type_add'),
    url(r'issue_type/(?P<pk>\d+)/update/$', IssueTypeUpdate.as_view(), name='issue_type_update'),
    url(r'issue_type/(?P<pk>\d+)/delete/$', IssueTypeDelete.as_view(), name='issue_type_delete'),

    # issue status
    url(r'^issue_statuses/$', IssueStatusList.as_view(), name='issue_status_list'),
    url(r'issue_status/(?P<pk>\d+)/$', IssueStatusDetail.as_view(), name='issue_status_detail'),
    url(r'issue_status/add/$', IssueStatusCreate.as_view(), name='issue_status_add'),
    url(r'issue_status/(?P<pk>\d+)/update/$', IssueStatusUpdate.as_view(), name='issue_status_update'),
    url(r'issue_status/(?P<pk>\d+)/delete/$', IssueStatusDelete.as_view(), name='issue_status_delete'),

    # version
    url(r'^versions/$', VersionList.as_view(), name='version_list'),
    url(r'^version/(?P<pk>\d+)/$', VersionDetail.as_view(), name='version_detail'),
    url(r'version/add/$', VersionCreate.as_view(), name='version_add'),
    url(r'version/(?P<pk>\d+)/update/$', VersionUpdate.as_view(), name='version_update'),
    url(r'version/(?P<pk>\d+)/delete/$', VersionDelete.as_view(), name='version_delete'),

    url(r'^admin/', include(admin.site.urls)),
]
