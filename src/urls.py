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
from project.views import user, project, issue, issue_status, issue_type, version, group


urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', TemplateView.as_view(template_name="index.html"), name='home'),

    # authentication
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}),
    url(r'^password_reset/$', auth_views.password_reset, {'password_reset_form': PasswordResetByEmailForm}),
    url('^', include('django.contrib.auth.urls')),

    # project
    url(r'^projects/$', project.List.as_view(), name='project_list'),
    url(r'^project/(?P<pk>\d+)/$', project.Detail.as_view(), name='project_detail'),
    url(r'project/add/$', project.Create.as_view(), name='project_add'),
    url(r'project/(?P<pk>\d+)/update/$', project.Update.as_view(), name='project_update'),
    url(r'project/(?P<pk>\d+)/delete/$', project.Delete.as_view(), name='project_delete'),
    url(r'project/(?P<pk>\d+)/members/$', project.ListMember.as_view(), name='member_list'),
    url(r'project/(?P<pk>\d+)/member/(?P<id>\d+)$', project.DeleteMember.as_view(), name='member_delete'),

    # issue
    url(r'^issues/$', issue.List.as_view(), name='issue_list'),
    url(r'^issue/(?P<pk>\d+)/$', issue.Detail.as_view(), name='issue_detail'),
    url(r'issue/add/$', issue.Create.as_view(), name='issue_add'),
    url(r'issue/(?P<pk>\d+)/update/$', issue.Update.as_view(), name='issue_update'),
    url(r'issue/(?P<pk>\d+)/delete/$', issue.Delete.as_view(), name='issue_delete'),
    url(r'comment/(?P<pk>\d+)/update/$', issue.CommentUpdate.as_view(), name='comment_update'),
    url(r'comment/(?P<pk>\d+)/delete/$', issue.CommentDelete.as_view(), name='comment_delete'),

    # issue type
    url(r'^issue_types/$', issue_type.List.as_view(), name='issue_type_list'),
    url(r'^issue_type/(?P<pk>\d+)/$', issue_type.Detail.as_view(), name='issue_type_detail'),
    url(r'issue_type/add/$', issue_type.Create.as_view(), name='issue_type_add'),
    url(r'issue_type/(?P<pk>\d+)/update/$', issue_type.Update.as_view(), name='issue_type_update'),
    url(r'issue_type/(?P<pk>\d+)/delete/$', issue_type.Delete.as_view(), name='issue_type_delete'),

    # issue status
    url(r'^issue_statuses/$', issue_status.List.as_view(), name='issue_status_list'),
    url(r'issue_status/(?P<pk>\d+)/$', issue_status.Detail.as_view(), name='issue_status_detail'),
    url(r'issue_status/add/$', issue_status.Create.as_view(), name='issue_status_add'),
    url(r'issue_status/(?P<pk>\d+)/update/$', issue_status.Update.as_view(), name='issue_status_update'),
    url(r'issue_status/(?P<pk>\d+)/delete/$', issue_status.Delete.as_view(), name='issue_status_delete'),

    # version
    url(r'^versions/$', version.List.as_view(), name='version_list'),
    url(r'^version/(?P<pk>\d+)/$', version.Detail.as_view(), name='version_detail'),
    url(r'version/add/$', version.Create.as_view(), name='version_add'),
    url(r'version/(?P<pk>\d+)/update/$', version.Update.as_view(), name='version_update'),
    url(r'version/(?P<pk>\d+)/delete/$', version.Delete.as_view(), name='version_delete'),

    # user
    url(r'^users/$', user.List.as_view(), name='user_list'),
    url(r'^user/(?P<pk>\d+)/$', user.Detail.as_view(), name='user_detail'),
    url(r'user/add/$', user.Create.as_view(), name='user_add'),
    url(r'user/(?P<pk>\d+)/update/$', user.Update.as_view(), name='user_update'),
    url(r'user/(?P<pk>\d+)/delete/$', user.Delete.as_view(), name='user_delete'),

    # group
    url(r'^groups/$', group.List.as_view(), name='group_list'),
    url(r'^group/(?P<pk>\d+)/$', group.Detail.as_view(), name='group_detail'),
    url(r'group/add/$', group.Create.as_view(), name='group_add'),
    url(r'group/(?P<pk>\d+)/update/$', group.Update.as_view(), name='group_update'),
    url(r'group/(?P<pk>\d+)/delete/$', group.Delete.as_view(), name='group_delete'),
    url(r'group/(?P<pk>\d+)/users/$', group.ListUser.as_view(), name='group_user_list'),
    url(r'group/(?P<pk>\d+)/user/(?P<id>\d+)$', group.DeleteUser.as_view(), name='group_user_delete'),

]
