from django.views.generic import ListView, DetailView, View, UpdateView, CreateView
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.http import HttpResponse
from ..models import Project, Project_Group_Role, Project_User_Role, Issue
from ..forms import ProjectForm, UpdateProjectForm
from .role import get_user_roles_id, get_role_users, get_role_user, get_user_groups_roles_id, \
    get_role_user_of_groups, check_user_in_groups, get_role_group, get_group_roles_id, get_active_roles
import json
from ..utils import Helper
from ..models import User
from .auth import PermissionMixin, SuperuserRequiredMixin, has_no_perm
from .base import CreateSuccessMessageMixin, UpdateSuccessMessageMixin, DeleteSuccessMessageMixin, \
    delete_success_message, create_success_message, decorate_object, update_success_message


_model = Project
_form = ProjectForm


def get_joined_projects(user):
    return [item.project for item in Project_User_Role.objects.filter(user_id=user.id)] + \
           [item.project for item in Project_Group_Role.objects.filter(group__in=user.groups.all())]


def get_visible_projects(user):
    if user.is_authenticated():
        if user.is_superuser:
            return Project.objects.all()
        else:
            return set(list(Project.objects.filter(is_public=True)) + get_joined_projects(user))
    else:
        return Project.objects.filter(is_public=True)


def get_hierarchical_list(objects):
    items = list(objects)

    def get_children(obj=None):
        child = list()
        for i in items:
            if obj == i.parent:
                child.append(get_children(i))
        return [obj or None, child or None]

    return get_children()[1]


def get_other_projects_html(project_id):
    projects = Project.objects.exclude(id=project_id)
    if not projects:
        return None

    items = get_hierarchical_list(projects)
    if not items:
        return None

    def get_html(data):
        for item in data:
            get_html.text += '''<li><a href="%s">%s%s</a></li>\n''' % \
                             (reverse('project_detail', kwargs={'pk': item[0].id}),
                              '&nbsp;' * get_html.depth * 4 +
                              "<i class='fa fa-angle-double-right'></i>" if get_html.depth else '',
                              Helper.limit_length(item[0].name, 30))
            if item[1] is not None:
                get_html.depth += 1
                get_html(item[1])
                get_html.depth -= 1

    get_html.text = ''
    get_html.depth = 0
    get_html(items)

    return get_html.text


class List(PermissionMixin, ListView):
    model = _model
    template_name = 'project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return self.get_all_projects_html()

    def get_all_projects_html(self):
        projects = get_visible_projects(self.request.user)
        joined_projects = get_joined_projects(self.request.user)
        if not projects:
            return None

        items = get_hierarchical_list(projects)
        if not items:
            return None

        def get_html(data):
            get_html.text += '''<ol style="list-style-type: none">\n'''
            for item in data:
                icon = '''<i class="fa %s"></i><i class="fa %s"></i>''' % \
                       (('fa-user font-yellow-casablanca' if item[0] in joined_projects else 'fa-none'),
                        ('fa-lock font-yellow-casablanca' if item[0].is_public is False else 'fa-none'))
                get_html.text += '''<li><a href="%s">%s<span>%s</span></a></li>\n''' % \
                                 (reverse('project_detail', kwargs={'pk': item[0].id}),
                                  icon,
                                  Helper.limit_length(item[0].name, 40))
                if item[1] is not None:
                    get_html(item[1])
            get_html.text += '</ol>\n'

        get_html.text = ''
        get_html(items)

        return get_html.text


class Detail(PermissionMixin, DetailView):
    model = _model
    template_name = 'project/overview.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['subprojects'] = Project.objects.filter(parent=self.object)
        context['role_users'] = get_role_users(self.kwargs['pk'])
        context['other_projects'] = get_other_projects_html(self.object.id)
        from ..models import IssueStatus
        context['IssueStatus'] = IssueStatus
        return context


class Create(SuperuserRequiredMixin, CreateSuccessMessageMixin, CreateView):
    model = _model
    template_name = 'create_project.html'
    form_class = _form
    success_url = reverse_lazy('project_list')

    def get_initial(self):
        initial = super(Create, self).get_initial().copy()
        initial['parent'] = self.request.GET.get('parent', None)        # create subproject, URL?parent=id
        return initial

    def get_form_kwargs(self):
        kwargs = super(Create, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['created_by'] = self.request.user.id
            kwargs.update({
                'data': data,
            })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Create, self).get_context_data(**kwargs)
        if 'backurl' in self.request.GET:
            context['backurl'] = reverse_lazy('admin_project')
        elif 'parent' in self.request.GET:
            context['backurl'] = reverse_lazy('project_detail', kwargs={'pk': self.request.GET['parent']})
        else:
            context['backurl'] = reverse_lazy('project_list')
        return context

    def get_success_url(self):
        if 'backurl' in self.request.GET:
            return reverse_lazy('admin_project')
        else:
            return reverse_lazy('project_list')


class Update(PermissionMixin, UpdateSuccessMessageMixin, UpdateView):
    model = _model
    template_name = 'project/settings/info.html'
    form_class = UpdateProjectForm

    def get_success_url(self):
        url = reverse('project_update', kwargs={'pk': self.object.pk})
        if 'backurl' in self.request.GET:
            url += '?backurl='
        return url

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        project_id = self.kwargs['pk']
        context['other_projects'] = get_other_projects_html(project_id)
        context['backurl'] = reverse_lazy('admin_project') if 'backurl' in self.request.GET else None
        return context

    def has_perm(self):
        user = self.request.user
        return user.has_perm('pm.change_project', Project.objects.get(pk=self.kwargs['pk']))


class Admin(SuperuserRequiredMixin, ListView):
    model = _model
    template_name = '_admin/projects.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super(Admin, self).get_context_data(**kwargs)
        context['order'] = self.order
        context['paging'] = {'length': self.length, 'offset': self.offset, 'page_length': self.page_length}
        return context

    def get_queryset(self):
        objects = self.model.objects.all().order_by("-updated_on")

        order = self.request.GET.get('order', None)
        if order in Helper.get_orderby_options(['name', 'is_public', 'updated_on']):
            objects = objects.order_by(order)
            self.order = order
        else:
            self.order = ""

        self.length = len(objects)
        self.offset = Helper.get_offset(self.request.GET.get('offset', None))
        from ..models import Settings
        self.page_length = Settings.get_page_length()

        return objects[self.offset:self.offset+self.page_length]


class Delete(SuperuserRequiredMixin, DeleteSuccessMessageMixin, DeleteView):
    model = _model
    template_name = '_admin/delete_project.html'
    success_url = reverse_lazy('admin_project')


class Settings(PermissionMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        user = self.request.user

        if user.has_perm('pm.change_project'):
            return redirect('project_update', pk=kwargs['pk'])

        elif user.has_perm('pm.manage_member', Project.objects.get(pk=pk)):
            return redirect('member_list', pk=kwargs['pk'])

        elif user.has_perm('pm.manage_version', Project.objects.get(pk=pk)):
            return redirect('version_list', pk=kwargs['pk'])

        elif user.has_perm('pm.manage_issue_category', Project.objects.get(pk=pk)):
            return redirect('issue_category_list', pk=kwargs['pk'])

        else:
            return has_no_perm(user)


class Close(PermissionMixin, View):
    def get(self, request, **kwargs):
        project = Project.objects.get(pk=kwargs['pk'])
        if project.OPEN_STATUS == project.status:
            project.status = project.CLOSED_STATUS
            project.save()
        return redirect('project_detail', pk=project.id)

    def has_perm(self):
        return self.request.user.has_perm('pm.close_project', Project.objects.get(pk=self.kwargs['pk']))


class Reopen(PermissionMixin, View):
    def get(self, request, **kwargs):
        project = Project.objects.get(pk=kwargs['pk'])
        if project.CLOSED_STATUS == project.status:
            project.status = project.OPEN_STATUS
            project.save()
        return redirect('project_detail', pk=project.id)

    def has_perm(self):
        return self.request.user.has_perm('pm.close_project', Project.objects.get(pk=self.kwargs['pk']))


class ListMember(PermissionMixin, View):
    template_name = 'project/settings/members.html'

    def get(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        project = Project.objects.get(id=project_id)

        context = dict()
        context['project'] = project
        context['other_projects'] = get_other_projects_html(project.id)

        role_user = get_role_user(project_id)
        users_id = [ i[1].id for i in role_user ]

        role_user_of_groups = get_role_user_of_groups(project_id)
        users_id_of_groups = list(set([ i[1].id for i in role_user_of_groups ]))

        all_role_user = list(set(role_user + role_user_of_groups))
        import collections
        tmp = collections.defaultdict(list)
        for item in all_role_user:
            tmp[item[1]].append(item[0])
        context['user_roles_deletable'] = [ (key,
                                             [ u for u in value ],
                                             False if key.id in users_id_of_groups else True )
                                            for key, value in tmp.iteritems() ]

        role_group = get_role_group(project_id)
        groups_id = list(set([ i[1].id for i in role_group ]))
        tmp = collections.defaultdict(list)
        for item in role_group:
            tmp[item[1]].append(item[0])
        context['group_roles'] = [ (key, [ u for u in value ]) for key, value in tmp.iteritems() ]

        context['not_joined_users'] = User.objects.all().exclude(id__in=list(set(users_id + users_id_of_groups)))
        context['not_joined_groups'] = Group.objects.all().exclude(id__in=groups_id)

        context['roles'] = get_active_roles()
        return render(request, self.template_name, context)

    def has_perm(self):
        project = Project.objects.get(pk=self.kwargs['pk'])
        user = self.request.user
        return user.has_perm('pm.manage_member', project)


class DeleteMember(PermissionMixin, View):
    def post(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        name = None

        if 'user_id' in request.GET:
            user_id = request.GET['user_id']
            name = User.objects.get(pk=user_id).get_full_name
            if check_user_in_groups(project_id, user_id) is False:
                Project_User_Role.objects.filter(project_id=project_id, user_id=user_id).delete()

        elif 'group_id' in request.GET:
            group_id = request.GET['group_id']
            name = str(Group.objects.get(pk=group_id))
            Project_Group_Role.objects.filter(project_id=project_id, group_id=group_id).delete()

        if name:
            from django.contrib import messages
            messages.success(self.request, delete_success_message % decorate_object(name))

        return redirect('member_list', pk=project_id)

    def has_perm(self):
        return self.request.user.has_perm('pm.manage_member', Project.objects.get(pk=self.kwargs['pk']))


class CreateMember(PermissionMixin, View):
    def post(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        users = request.POST.getlist('user')
        groups = request.POST.getlist('group')
        roles = request.POST.getlist('role')

        if (users or groups) and roles:
            for id in users:
                for r in roles:
                    Project_User_Role(project_id=project_id, user_id=id, role_id=r).save()

            for id in groups:
                for r in roles:
                    Project_Group_Role(project_id=project_id, group_id=id, role_id=r).save()

            from django.contrib import messages
            messages.success(self.request, create_success_message % 'member')

        return redirect('member_list', pk=project_id)

    def has_perm(self):
        return self.request.user.has_perm('pm.manage_member', Project.objects.get(pk=self.kwargs['pk']))


class MemberRoles(View):
    def get(self, request, *args, **kwargs):
        project_id = kwargs['pk']

        data = dict()
        data['all'] = [{'id': n.id, 'name': n.name} for n in get_active_roles()]

        if 'user_id' in request.GET:
            user_id = request.GET['user_id']
            data['selected'] = list(set(get_user_roles_id(project_id, user_id) +
                                        get_user_groups_roles_id(project_id, user_id)))
            data['disabled'] = get_user_groups_roles_id(project_id, user_id)

        elif 'group_id' in request.GET:
            group_id = request.GET['group_id']
            data['selected'] = get_group_roles_id(project_id, group_id)

        return HttpResponse(json.dumps(data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        data = set(map(int, request.POST.getlist('item')))

        if 'user_id' in request.GET:
            user_id = request.GET['user_id']
            old_of_user = set(get_user_roles_id(project_id, user_id))
            old_of_groups = set(get_user_groups_roles_id(project_id, user_id))
            old = old_of_user - old_of_groups
            new = data - old_of_groups

            select = list(new - old)
            unselect = list(old - new)

            for n in select:
                Project_User_Role(project_id=project_id, user_id=user_id, role_id=n).save()
            Project_User_Role.objects.filter(project_id=project_id, user_id=user_id, role_id__in=unselect).delete()

            from django.contrib import messages
            messages.success(self.request, update_success_message % decorate_object(User.objects.get(pk=user_id)))

        elif 'group_id' in request.GET:
            group_id = request.GET['group_id']
            old = set(get_group_roles_id(project_id, group_id))
            new = data

            select = list(new - old)
            unselect = list(old - new)

            for n in select:
                Project_Group_Role(project_id=project_id, group_id=group_id, role_id=n).save()
            Project_Group_Role.objects.filter(project_id=project_id, group_id=group_id, role_id__in=unselect).delete()

            from django.contrib import messages
            messages.success(self.request, update_success_message % decorate_object(Group.objects.get(pk=group_id)))

        return redirect('member_list', pk=project_id)


class Gantt(PermissionMixin, View):
    def get(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        project = Project.objects.get(id=project_id)

        context = dict()
        context['project'] = project
        context['other_projects'] = get_other_projects_html(project.id)

        parent_str = "{{name: '{name}', 'children': {children}, content: '<a href=\"{url}\">{name}</a>', " \
                     "tasks: [{{color: '#F1C232', from: new Date({from_year},{from_month},{from_day},0,0,0), " \
                     "to: new Date({to_year},{to_month},{to_day},24,0,0), " \
                     "_from: '{from_month}.{from_day}', _to: '{to_month}.{to_day}', " \
                     "_status: '{status}', _assignee: '{assigned_to}', progress: {done_ratio}}}]}},\n"

        leaf_node_str = "{{name: '{name}', content: '<a href=\"{url}\">{name}</a>', " \
                        "tasks: [{{color: '#F1C232', from: new Date({from_year},{from_month},{from_day},0,0,0), " \
                        "to: new Date({to_year},{to_month},{to_day},24,0,0), " \
                        "_from: '{from_month}.{from_day}', _to: '{to_month}.{to_day}', " \
                        "_status: '{status}', _assignee: '{assigned_to}', progress: {done_ratio}}}]}},\n"

        import json

        def get_data(items):
            for item in items:
                issue = item[0]
                if item[1] is not None:
                    get_data.text += parent_str.format(
                        name=issue.id,
                        children=json.dumps([str(i[0].id) for i in item[1]]),
                        url=reverse('issue_detail', kwargs={'pk': issue.id}),
                        from_year=issue.start_date.year if issue.start_date else 0,
                        from_month=issue.start_date.month-1 if issue.start_date else 0,
                        from_day=issue.start_date.day if issue.start_date else 0,
                        to_year=issue.due_date.year if issue.due_date else 0,
                        to_month=issue.due_date.month-1 if issue.due_date else 0,
                        to_day=issue.due_date.day if issue.due_date else 0,
                        status=issue.status.name,
                        assigned_to=issue.assigned_to.username if issue.assigned_to else None,
                        done_ratio=issue.done_ratio)
                    get_data(item[1])
                else:
                    get_data.text += leaf_node_str.format(
                        name=issue.id,
                        url=reverse('issue_detail', kwargs={'pk': issue.id}),
                        from_year=issue.start_date.year if issue.start_date else 0,
                        from_month=issue.start_date.month-1 if issue.start_date else 0,
                        from_day=issue.start_date.day if issue.start_date else 0,
                        to_year=issue.due_date.year if issue.due_date else 0,
                        to_month=issue.due_date.month-1 if issue.due_date else 0,
                        to_day=issue.due_date.day if issue.due_date else 0,
                        status=issue.status.name,
                        assigned_to=issue.assigned_to.username if issue.assigned_to else None,
                        done_ratio=issue.done_ratio)

        get_data.text = ''

        projects = Issue.objects.filter(project=project)
        if not projects:
            context['gantt_data'] = None
        else:
            get_data(get_hierarchical_list(projects))
            context['gantt_data'] = get_data.text

        from datetime import date
        now = date.today()
        context['now_year'] = now.year
        context['now_month'] = now.month-1
        context['now_day'] = now.day

        return render(request, 'project/gantt.html', context)

    def has_perm(self):
        return self.request.user.has_perm('pm.read_gantt', Project.objects.get(pk=self.kwargs['pk']))
