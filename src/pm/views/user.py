from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import Group
from django.shortcuts import redirect, HttpResponseRedirect, HttpResponse
from ..forms import UserForm, UpdateUserForm
from ..models import Project, Role, Project_User_Role, User
from .role import get_project_role_of_user, get_project_role_of_groups, get_user_roles_id, get_user_groups_roles_id, \
    get_active_roles
from .base import CreateSuccessMessageMixin, DeleteSuccessMessageMixin, UpdateSuccessMessageMixin
from .auth import SuperuserRequiredMixin
import json


_model = User
_form = UserForm


class List(SuperuserRequiredMixin, ListView):
    model = _model
    template_name = '_admin/users.html'
    context_object_name = 'users'


class Detail(SuperuserRequiredMixin, DetailView):
    model = _model
    template_name = 'user_info.html'
    context_object_name = 'account'     # conflict with login 'user'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        user = self.object
        project_role = list(set(get_project_role_of_user(user.id) + get_project_role_of_groups(user)))

        import collections
        tmp = collections.defaultdict(list)
        for item in project_role:
            tmp[item[0]].append(item[1])

        context['project_roles'] = [ ( key, ( r for r in value ) ) for key, value in tmp.iteritems() ]
        return context


class Create(SuperuserRequiredMixin, CreateSuccessMessageMixin, CreateView):
    model = _model
    form_class = _form
    template_name = '_admin/create_user.html'
    success_url = reverse_lazy('user_list')


class Update(SuperuserRequiredMixin, UpdateSuccessMessageMixin, UpdateView):
    model = _model
    template_name = '_admin/edit_user.html'
    form_class = UpdateUserForm
    context_object_name = 'account'     # conflict with login 'user'

    def get_form_kwargs(self):
        kwargs = super(Update, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['username'] = self.object.username
            kwargs.update({
                'data': data,
            })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        user = self.object

        project_role_of_user = get_project_role_of_user(user.id)
        project_role_of_group = get_project_role_of_groups(user)
        project_role_of_all = list(set(project_role_of_user + project_role_of_group))

        import collections
        tmp = collections.defaultdict(list)
        for item in project_role_of_all:
            tmp[item[0]].append(item[1])

        projects_of_group = list(set([ i[0] for i in project_role_of_group ]))
        context['project_roles_deletable'] = [ ( key,
                                                 ( r for r in value ),
                                                 False if key in projects_of_group else True )
                                               for key, value in tmp.iteritems() ]

        context['not_joined_projects'] = Project.objects.all()\
            .exclude(id__in=list(set([ i[0].id for i in project_role_of_all ])))

        context['joined_groups'] = user.groups.all()
        groups = Group.objects.all()
        context['not_joined_groups'] = list(set(groups)-set(context['joined_groups']))

        context['roles'] = get_active_roles()
        return context

    def get_success_url(self):
        return reverse_lazy('user_update', kwargs={'pk': self.object.id})


class Delete(SuperuserRequiredMixin, DeleteSuccessMessageMixin, DeleteView):
    model = _model
    success_url = reverse_lazy('user_list')

    def get(self, request, *args, **kwargs):
        return redirect('user_list')


class Lock(SuperuserRequiredMixin, View):
    def get(self, request, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        if user.is_active:
            user.is_active = False
            user.save()
        return redirect('user_list')


class Unlock(SuperuserRequiredMixin, View):
    def get(self, request, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        if not user.is_active:
            user.is_active = True
            user.save()
        return redirect('user_list')


class JoinProjects(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        projects = request.POST.getlist('project')
        roles = request.POST.getlist('role')

        if len(projects) and len(roles):
            for p in projects:
                for r in roles:
                    Project_User_Role(project_id=p, user_id=user_id, role_id=r).save()

        return HttpResponseRedirect(reverse('user_update', args=(user_id,))+'#tab_user_project')


class QuitProject(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        project_id = kwargs['id']
        Project_User_Role.objects.filter(project_id=project_id, user_id=user_id).delete()
        return HttpResponseRedirect(reverse('user_update', args=(user_id,))+'#tab_user_project')


class JoinGroups(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        join_groups = request.POST.getlist('group')
        through = User.groups.through
        through.objects.bulk_create([ through(user_id=pk, group_id=id) for id in join_groups ])
        return HttpResponseRedirect(reverse('user_update', args=(pk,))+'#tab_user_group')


class QuitGroup(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        User.groups.through.objects.filter(user_id=kwargs['pk'], group_id=kwargs['id']).delete()
        return HttpResponseRedirect(reverse('user_update', args=(kwargs['pk'],))+'#tab_user_group')


class Roles(View):
    def get(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        project_id = kwargs['id']

        data = dict()
        data['all'] = [{'id': n.id, 'name': n.name} for n in get_active_roles()]
        data['selected'] = list(set(get_user_roles_id(project_id, user_id) +
                                    get_user_groups_roles_id(project_id, user_id)))
        data['disabled'] = list(get_user_groups_roles_id(project_id, user_id))

        return HttpResponse(json.dumps(data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        project_id = kwargs['id']

        old_of_user = set(get_user_roles_id(project_id, user_id))
        old_of_group = set(get_user_groups_roles_id(project_id, user_id))
        old = old_of_user - old_of_group
        new = set(map(int, request.POST.getlist('item'))) - old_of_group

        select = list(new - old)
        unselect = list(old - new)

        for n in select:
            Project_User_Role(project_id=project_id, user_id=user_id, role_id=n).save()
        Project_User_Role.objects.filter(project_id=project_id, user_id=user_id, role_id__in=unselect).delete()

        return HttpResponseRedirect(reverse('user_update', args=(user_id,))+'#tab_user_project')
