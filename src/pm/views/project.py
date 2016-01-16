from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, HttpResponse
from ..models import Project, Role, Project_Group_Role, Project_User_Role
from ..forms import ProjectForm, UpdateProjectForm
from .role import get_user_roles_id, get_role_users, get_role_user, get_user_groups_roles_id, \
    get_role_user_of_groups, check_user_in_groups, get_role_group, get_group_roles_id
import json


_model = Project
_form = ProjectForm


class List(ListView):
    model = _model
    template_name = 'project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        self.projects = Project.objects.all()
        import json
        return json.dumps(self.get_children()[1])

    def get_children(self, project=None):
        child = list()
        for p in self.projects:
            if project == p.parent:
                child.append(self.get_children(p))
        return [{ 'name':project.name,
                  'url': reverse('project_detail', kwargs={'pk': project.pk}),
                  'my_project': True if self.request.user == project.created_by else False }
                if project else None, child]


class Detail(DetailView):
    model = _model
    template_name = 'project/overview.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['subprojects'] = Project.objects.filter(parent=self.object)
        context['role_users'] = get_role_users(self.kwargs['pk'])
        return context


class Create(CreateView):
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


class Update(UpdateView):
    model = _model
    template_name = 'project/settings/info.html'
    form_class = UpdateProjectForm

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})


class Admin(ListView):
    model = _model
    template_name = '_admin/projects.html'
    context_object_name = 'projects'


class Delete(DeleteView):
    model = _model
    template_name = '_admin/delete_project.html'
    success_url = reverse_lazy('admin_project')


class Close(View):
    def get(self, request, **kwargs):
        project = Project.objects.get(pk=kwargs['pk'])
        if project.OPEN_STATUS == project.status:
            project.status = project.CLOSED_STATUS
            project.save()
        return redirect('project_detail', pk=project.id)


class Reopen(View):
    def get(self, request, **kwargs):
        project = Project.objects.get(pk=kwargs['pk'])
        if project.CLOSED_STATUS == project.status:
            project.status = project.OPEN_STATUS
            project.save()
        return redirect('project_detail', pk=project.id)


class ListMember(View):
    template_name = 'project/settings/members.html'

    def get(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        project = Project.objects.get(id=project_id)

        context = dict()
        context['project'] = project

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

        context['roles'] = Role.objects.all()
        return render(request, self.template_name, context)


class DeleteMember(View):
    def post(self, request, *args, **kwargs):
        project_id = kwargs['pk']

        if 'user_id' in request.GET:
            user_id = request.GET['user_id']
            if check_user_in_groups(project_id, user_id) is False:
                Project_User_Role.objects.filter(project_id=project_id, user_id=user_id).delete()

        elif 'group_id' in request.GET:
            group_id = request.GET['group_id']
            Project_Group_Role.objects.filter(project_id=project_id, group_id=group_id).delete()

        return redirect('member_list', pk=project_id)


class CreateMember(View):
    def post(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        users = request.POST.getlist('user')
        groups = request.POST.getlist('group')
        roles = request.POST.getlist('role')
        for id in users:
            for r in roles:
                Project_User_Role(project_id=project_id, user_id=id, role_id=r).save()

        for id in groups:
            for r in roles:
                Project_Group_Role(project_id=project_id, group_id=id, role_id=r).save()

        return redirect('member_list', pk=project_id)


class MemberRoles(View):
    def get(self, request, *args, **kwargs):
        project_id = kwargs['pk']

        data = dict()
        data['all'] = [ {'id':n.id, 'name':n.name} for n in Role.objects.all() ]

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

        elif 'group_id' in request.GET:
            group_id = request.GET['group_id']
            old = set(get_group_roles_id(project_id, group_id))
            new = data

            select = list(new - old)
            unselect = list(old - new)

            for n in select:
                Project_Group_Role(project_id=project_id, group_id=group_id, role_id=n).save()
            Project_Group_Role.objects.filter(project_id=project_id, group_id=group_id, role_id__in=unselect).delete()

        return redirect('member_list', pk=project_id)