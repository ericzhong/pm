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
from pm.forms import PasswordResetByEmailForm
from pm.views import user, project, issue, issue_status, issue_tag, version, group, role


urlpatterns = [

    url(r'^$', TemplateView.as_view(template_name="index.html"), name='home'),
    url(r'^admin/$', project.Admin.as_view(), name='admin'),

    # authentication
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}),
    url(r'^password_reset/$', auth_views.password_reset, {'password_reset_form': PasswordResetByEmailForm}),
    url('^', include('django.contrib.auth.urls')),

    # project
    url(r'^projects/$', project.List.as_view(), name='project_list'),
    url(r'^projects/(?P<pk>\d+)/$', project.Detail.as_view(), name='project_detail'),
    url(r'^projects/add/$', project.Create.as_view(), name='project_add'),
    url(r'^projects/(?P<pk>\d+)/settings/$', project.Update.as_view(), name='project_settings'),
    url(r'^projects/(?P<pk>\d+)/settings/info/$', project.Update.as_view(), name='project_update'),
    url(r'^admin/projects/$', project.Admin.as_view(), name='admin_project'),
    url(r'^projects/(?P<pk>\d+)/delete/$', project.Delete.as_view(), name='project_delete'),
    url(r'^projects/(?P<pk>\d+)/close/$', project.Close.as_view(), name='project_close'),
    url(r'^projects/(?P<pk>\d+)/reopen/$', project.Reopen.as_view(), name='project_reopen'),

    #url(r'^projects/(?P<pk>\d+)/members/$', project.ListMember.as_view(), name='member_list'),
    #url(r'^projects/(?P<pk>\d+)/member/(?P<id>\d+)$', project.DeleteMember.as_view(), name='member_delete'),

    # issue tag
    url(r'^issue_tags/$', issue_tag.List.as_view(), name='issue_tag_list'),
    url(r'^issue_tags/add/$', issue_tag.Create.as_view(), name='issue_tag_add'),
    url(r'^issue_tags/(?P<pk>\d+)/update/$', issue_tag.Update.as_view(), name='issue_tag_update'),
    url(r'^issue_tags/(?P<pk>\d+)/delete/$', issue_tag.Delete.as_view(), name='issue_tag_delete'),

    # issue status
    url(r'^issue_statuses/$', issue_status.List.as_view(), name='issue_status_list'),
    url(r'^issue_statuses/add/$', issue_status.Create.as_view(), name='issue_status_add'),
    url(r'^issue_statuses/(?P<pk>\d+)/update/$', issue_status.Update.as_view(), name='issue_status_update'),
    url(r'^issue_statuses/(?P<pk>\d+)/delete/$', issue_status.Delete.as_view(), name='issue_status_delete'),

    # issue
    url(r'^projects/(?P<pk>\d+)/issues/$', issue.List.as_view(), name='issue_list'),
    url(r'^projects/(?P<pk>\d+)/issues/add/$', issue.Create.as_view(), name='issue_add'),
    url(r'^issues/(?P<pk>\d+)/$', issue.Detail.as_view(), name='issue_detail'),
    url(r'^issues/(?P<pk>\d+)/update/$', issue.Update.as_view(), name='issue_update'),
    url(r'^issues/(?P<pk>\d+)/delete/$', issue.Delete.as_view(), name='issue_delete'),
    url(r'^issues/(?P<pk>\d+)/quote/$', issue.Quote.as_view(), name='issue_quote'),
    url(r'^comment/(?P<pk>\d+)/update/$', issue.CommentUpdate.as_view(), name='comment_update'),
    url(r'^issues/$', issue.AllIssues.as_view(), name='issue_all'),
    url(r'^mypage/$', issue.MyPage.as_view(), name='my_page'),

    # worktime
    url(r'^issues/(?P<pk>\d+)/worktimes/$', issue.WorktimeList.as_view(), name='worktime_list'),
    url(r'^issues/(?P<pk>\d+)/worktimes/add$', issue.WorktimeCreate.as_view(), name='worktime_add'),
    url(r'^worktimes/(?P<pk>\d+)/update/$', issue.WorktimeUpdate.as_view(), name='worktime_update'),
    url(r'^worktimes/(?P<pk>\d+)/delete/$', issue.WorktimeDelete.as_view(), name='worktime_delete'),

    # version
    url(r'^projects/(?P<pk>\d+)/roadmap/$', version.Roadmap.as_view(), name='version_roadmap'),
    url(r'^projects/(?P<pk>\d+)/settings/versions/$', version.List.as_view(), name='version_list'),
    url(r'^projects/(?P<pk>\d+)/versions/add/$', version.Create.as_view(), name='version_add'),
    url(r'^versions/(?P<pk>\d+)/$', version.Detail.as_view(), name='version_detail'),
    url(r'^versions/(?P<pk>\d+)/update/$', version.Update.as_view(), name='version_update'),
    url(r'^versions/(?P<pk>\d+)/delete/$', version.Delete.as_view(), name='version_delete'),

    # user
    url(r'^users/$', user.List.as_view(), name='user_list'),
    url(r'^users/add/$', user.Create.as_view(), name='user_add'),
    #url(r'^users/(?P<pk>\d+)/$', user.Detail.as_view(), name='user_detail'),
    url(r'^users/(?P<pk>\d+)/update/$', user.Update.as_view(), name='user_update'),
    url(r'^users/(?P<pk>\d+)/delete/$', user.Delete.as_view(), name='user_delete'),
    url(r'^users/(?P<pk>\d+)/lock/$', user.Lock.as_view(), name='user_lock'),
    url(r'^users/(?P<pk>\d+)/unlock/$', user.Unlock.as_view(), name='user_unlock'),
    url(r'^users/(?P<pk>\d+)/join_projects/$', user.JoinProjects.as_view(), name='user_join_projects'),
    url(r'^users/(?P<pk>\d+)/quit_project/(?P<id>\d+)$', user.QuitProject.as_view(), name='user_quit_project'),
    url(r'^users/(?P<pk>\d+)/join_groups/$', user.JoinGroups.as_view(), name='user_join_groups'),
    url(r'^users/(?P<pk>\d+)/quit_group/(?P<id>\d+)$', user.QuitGroup.as_view(), name='user_quit_group'),

    # group
    url(r'^groups/$', group.List.as_view(), name='group_list'),
    url(r'^groups/add/$', group.Create.as_view(), name='group_add'),
    url(r'^groups/(?P<pk>\d+)/update/$', group.Update.as_view(), name='group_update'),
    url(r'^groups/(?P<pk>\d+)/delete/$', group.Delete.as_view(), name='group_delete'),
    url(r'^groups/(?P<pk>\d+)/add_users/$', group.AddUsers.as_view(), name='group_add_users'),
    url(r'^groups/(?P<pk>\d+)/delete_user/(?P<id>\d+)$', group.DeleteUser.as_view(), name='group_delete_user'),
    url(r'^groups/(?P<pk>\d+)/join_projects/$', group.JoinProjects.as_view(), name='group_join_projects'),
    url(r'^groups/(?P<pk>\d+)/quit_project/(?P<id>\d+)$', group.QuitProject.as_view(), name='group_quit_project'),

    # Role
    url(r'^roles/$', role.List.as_view(), name='role_list'),
    url(r'^roles/add/$', role.Create.as_view(), name='role_add'),
    url(r'^roles/(?P<pk>\d+)/update/$', role.Update.as_view(), name='role_update'),
    url(r'^roles/(?P<pk>\d+)/delete/$', role.Delete.as_view(), name='role_delete'),

    url(r'^django-admin/', include(admin.site.urls)),
]