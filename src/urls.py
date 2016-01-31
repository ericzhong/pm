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
from django.contrib.auth.decorators import login_required

from pm.views import user, project, issue, issue_status, issue_tag, version, group, role, setting, \
    issue_category, base, account

from pm.views.base import admin_required, anonymous_perm

urlpatterns = [
    url(r'^$', base.homepage.as_view(), name='homepage'),

    # authentication
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^my/password$', auth_views.password_change,
        {'template_name': 'password.html', 'post_change_redirect': '/my/password'}, name='password_change'),

    # account
    url(r'^my/account$', login_required(account.MyAccount.as_view()), name='my_account'),
    url(r'^my/avatar$', login_required(account.MyAvatar.as_view()), name='my_avatar'),

    # project
    url(r'^projects/$', anonymous_perm(project.List.as_view()), name='project_list'),
    url(r'^projects/(?P<pk>\d+)/$', anonymous_perm(project.Detail.as_view()), name='project_detail'),
    url(r'^projects/add/$', login_required(project.Create.as_view()), name='project_add'),
    url(r'^projects/(?P<pk>\d+)/delete/$', login_required(project.Delete.as_view()), name='project_delete'),
    url(r'^projects/(?P<pk>\d+)/close/$', login_required(project.Close.as_view()), name='project_close'),
    url(r'^projects/(?P<pk>\d+)/reopen/$', login_required(project.Reopen.as_view()), name='project_reopen'),
    url(r'^projects/(?P<pk>\d+)/gantt/$', anonymous_perm(project.Gantt.as_view()), name='project_gantt'),

    # project settings
    url(r'^projects/(?P<pk>\d+)/settings/$', login_required(project.Update.as_view()), name='project_settings'),
    url(r'^projects/(?P<pk>\d+)/settings/info/$', login_required(project.Update.as_view()), name='project_update'),
    url(r'^projects/(?P<pk>\d+)/settings/versions/$', login_required(version.List.as_view()), name='version_list'),
    url(r'^projects/(?P<pk>\d+)/settings/members/$', login_required(project.ListMember.as_view()), name='member_list'),
    url(r'^projects/(?P<pk>\d+)/settings/issue_categories/$', login_required(issue_category.List.as_view()), name='issue_category_list'),

    # member
    url(r'^projects/(?P<pk>\d+)/members/delete$', login_required(project.DeleteMember.as_view()), name='member_delete'),
    url(r'^projects/(?P<pk>\d+)/members/add$', login_required(project.CreateMember.as_view()), name='member_add'),
    url(r'^projects/(?P<pk>\d+)/members/roles$', anonymous_perm(project.MemberRoles.as_view()), name='member_roles'),

    # issue category
    url(r'^projects/(?P<pk>\d+)/issue_categories/add/$', login_required(issue_category.Create.as_view()), name='issue_category_add'),
    url(r'^issue_categories/(?P<pk>\d+)/update/$', login_required(issue_category.Update.as_view()), name='issue_category_update'),
    url(r'^issue_categories/(?P<pk>\d+)/delete/$', login_required(issue_category.Delete.as_view()), name='issue_category_delete'),

    # issue tag
    url(r'^issue_tags/$', login_required(admin_required(issue_tag.List.as_view())), name='issue_tag_list'),
    url(r'^issue_tags/add/$', login_required(issue_tag.Create.as_view()), name='issue_tag_add'),
    url(r'^issue_tags/(?P<pk>\d+)/update/$', login_required(issue_tag.Update.as_view()), name='issue_tag_update'),
    url(r'^issue_tags/(?P<pk>\d+)/delete/$', login_required(issue_tag.Delete.as_view()), name='issue_tag_delete'),

    # issue status
    url(r'^issue_statuses/$', login_required(admin_required(issue_status.List.as_view())), name='issue_status_list'),
    url(r'^issue_statuses/add/$', login_required(issue_status.Create.as_view()), name='issue_status_add'),
    url(r'^issue_statuses/(?P<pk>\d+)/update/$', login_required(issue_status.Update.as_view()), name='issue_status_update'),
    url(r'^issue_statuses/(?P<pk>\d+)/delete/$', login_required(issue_status.Delete.as_view()), name='issue_status_delete'),

    # issue
    url(r'^projects/(?P<pk>\d+)/issues/$', anonymous_perm(issue.List.as_view()), name='issue_list'),
    url(r'^projects/(?P<pk>\d+)/issues/add/$', login_required(issue.Create.as_view()), name='issue_add'),
    url(r'^issues/(?P<pk>\d+)/$', anonymous_perm(issue.Detail.as_view()), name='issue_detail'),
    url(r'^issues/(?P<pk>\d+)/update/$', login_required(issue.Update.as_view()), name='issue_update'),
    url(r'^issues/(?P<pk>\d+)/delete/$', login_required(issue.Delete.as_view()), name='issue_delete'),
    url(r'^issues/(?P<pk>\d+)/quote/$', login_required(issue.Quote.as_view()), name='issue_quote'),
    url(r'^issues/(?P<pk>\d+)/watch/$', login_required(issue.Watch.as_view()), name='issue_watch'),
    url(r'^issues/(?P<pk>\d+)/unwatch/$', login_required(issue.Unwatch.as_view()), name='issue_unwatch'),
    url(r'^comments/(?P<pk>\d+)/update/$', login_required(issue.CommentUpdate.as_view()), name='comment_update'),
    url(r'^issues/$', anonymous_perm(issue.AllIssues.as_view()), name='issue_all'),
    url(r'^mypage/$', login_required(issue.MyPage.as_view()), name='my_page'),

    # worktime
    url(r'^issues/(?P<pk>\d+)/worktimes/$', anonymous_perm(issue.WorktimeList.as_view()), name='worktime_list'),
    url(r'^issues/(?P<pk>\d+)/worktimes/add$', login_required(issue.WorktimeCreate.as_view()), name='worktime_add'),
    url(r'^worktimes/(?P<pk>\d+)/update/$', login_required(issue.WorktimeUpdate.as_view()), name='worktime_update'),
    url(r'^worktimes/(?P<pk>\d+)/delete/$', login_required(issue.WorktimeDelete.as_view()), name='worktime_delete'),

    # version
    url(r'^projects/(?P<pk>\d+)/roadmap/$', anonymous_perm(version.Roadmap.as_view()), name='version_roadmap'),
    url(r'^projects/(?P<pk>\d+)/versions/add/$', login_required(version.Create.as_view()), name='version_add'),
    url(r'^versions/(?P<pk>\d+)/$', anonymous_perm(version.Detail.as_view()), name='version_detail'),
    url(r'^versions/(?P<pk>\d+)/update/$', login_required(version.Update.as_view()), name='version_update'),
    url(r'^versions/(?P<pk>\d+)/delete/$', login_required(version.Delete.as_view()), name='version_delete'),

    # user
    url(r'^users/$', login_required(admin_required(user.List.as_view())), name='user_list'),
    url(r'^users/add/$', login_required(admin_required(user.Create.as_view())), name='user_add'),
    url(r'^users/(?P<pk>\d+)/$', anonymous_perm(user.Detail.as_view()), name='user_detail'),
    url(r'^users/(?P<pk>\d+)/update/$', login_required(admin_required(user.Update.as_view())), name='user_update'),
    url(r'^users/(?P<pk>\d+)/delete/$', login_required(admin_required(user.Delete.as_view())), name='user_delete'),
    url(r'^users/(?P<pk>\d+)/lock/$', login_required(admin_required(user.Lock.as_view())), name='user_lock'),
    url(r'^users/(?P<pk>\d+)/unlock/$', login_required(admin_required(user.Unlock.as_view())), name='user_unlock'),
    url(r'^users/(?P<pk>\d+)/join_projects/$', login_required(user.JoinProjects.as_view()), name='user_join_projects'),
    url(r'^users/(?P<pk>\d+)/quit_project/(?P<id>\d+)$', login_required(user.QuitProject.as_view()), name='user_quit_project'),
    url(r'^users/(?P<pk>\d+)/join_groups/$', login_required(user.JoinGroups.as_view()), name='user_join_groups'),
    url(r'^users/(?P<pk>\d+)/quit_group/(?P<id>\d+)$', login_required(user.QuitGroup.as_view()), name='user_quit_group'),
    url(r'^users/(?P<pk>\d+)/projects/(?P<id>\d+)/roles$', anonymous_perm(user.Roles.as_view()), name='user_roles'),

    # group
    url(r'^groups/$', login_required(admin_required(group.List.as_view())), name='group_list'),
    url(r'^groups/add/$', login_required(admin_required(group.Create.as_view())), name='group_add'),
    url(r'^groups/(?P<pk>\d+)/update/$', login_required(admin_required(group.Update.as_view())), name='group_update'),
    url(r'^groups/(?P<pk>\d+)/delete/$', login_required(admin_required(group.Delete.as_view())), name='group_delete'),
    url(r'^groups/(?P<pk>\d+)/add_users/$', login_required(admin_required(group.AddUsers.as_view())), name='group_add_users'),
    url(r'^groups/(?P<pk>\d+)/delete_user/(?P<id>\d+)$', login_required(admin_required(group.DeleteUser.as_view())), name='group_delete_user'),
    url(r'^groups/(?P<pk>\d+)/join_projects/$', login_required(group.JoinProjects.as_view()), name='group_join_projects'),
    url(r'^groups/(?P<pk>\d+)/quit_project/(?P<id>\d+)$', login_required(group.QuitProject.as_view()), name='group_quit_project'),
    url(r'^groups/(?P<pk>\d+)/projects/(?P<id>\d+)/roles$', login_required(group.Roles.as_view()), name='group_roles'),

    # role
    url(r'^roles/$', login_required(admin_required(role.List.as_view())), name='role_list'),
    url(r'^roles/add/$', login_required(admin_required(role.Create.as_view())), name='role_add'),
    url(r'^roles/(?P<pk>\d+)/update/$', login_required(admin_required(role.Update.as_view())), name='role_update'),
    url(r'^roles/(?P<pk>\d+)/delete/$', login_required(admin_required(role.Delete.as_view())), name='role_delete'),

    # settings
    url(r'^settings/$', login_required(admin_required(setting.Setting.as_view())), name='settings'),
    url(r'^admin/$', login_required(admin_required(project.Admin.as_view())), name='admin'),
    url(r'^admin/projects/$', login_required(admin_required(project.Admin.as_view())), name='admin_project'),

    url(r'^django-admin/', include(admin.site.urls)),
]
