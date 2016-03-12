from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import Group
from django.shortcuts import redirect, HttpResponseRedirect, HttpResponse
from ..forms import GroupForm
from ..models import Project, Role, Project_Group_Role, User
from .role import get_group_roles_id, get_project_role_of_group, get_active_roles
from .base import CreateSuccessMessageMixin, DeleteSuccessMessageMixin, UpdateSuccessMessageMixin
from .auth import SuperuserRequiredMixin
import json


_model = Group
_form = GroupForm


class List(SuperuserRequiredMixin, ListView):
    model = _model
    template_name = '_admin/groups.html'
    context_object_name = 'groups'


class Detail(SuperuserRequiredMixin, DetailView):
    model = _model
    template_name = '_admin/groups.html'
    context_object_name = 'group'


class Create(SuperuserRequiredMixin, CreateSuccessMessageMixin, CreateView):
    model = _model
    form_class = _form
    template_name = '_admin/create_group.html'

    def get_success_url(self):
        if 'continue' in self.request.POST:
            return reverse_lazy('group_add')
        else:
            return reverse_lazy('group_list')


class Update(SuperuserRequiredMixin, UpdateSuccessMessageMixin, UpdateView):
    model = _model
    form_class = _form
    template_name = '_admin/edit_group.html'

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        group = self.object

        joined_users = group.user_set.all()
        context['joined_users'] = joined_users
        context['not_joined_users'] = User.objects.all().exclude(id__in=[ n.id for n in joined_users ])

        project_role_of_group = get_project_role_of_group(group.id)
        import collections
        tmp = collections.defaultdict(list)
        for item in project_role_of_group:
            tmp[item[0]].append(item[1])
        context['project_roles'] = [ ( key, ( r for r in value ) ) for key, value in tmp.iteritems() ]
        joined_projects = list(set([ i[0].id for i in project_role_of_group ]))
        context['not_joined_projects'] = Project.objects.all().exclude(id__in=joined_projects)

        context['roles'] = get_active_roles()
        return context

    def get_success_url(self):
        return reverse_lazy('group_update', kwargs={'pk': self.object.id})


class Delete(SuperuserRequiredMixin, DeleteSuccessMessageMixin, DeleteView):
    model = _model
    success_url = reverse_lazy('group_list')

    def get(self, request, *args, **kwargs):
        return redirect('group_list')


class AddUsers(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        add_users = request.POST.getlist('user')
        through = User.groups.through
        through.objects.bulk_create([ through(user_id=id, group_id=pk) for id in add_users ])
        return HttpResponseRedirect(reverse('group_update', args=(pk,))+'#tab_group_user')


class DeleteUser(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        User.groups.through.objects.filter(user_id=kwargs['id'], group_id=kwargs['pk']).delete()
        return HttpResponseRedirect(reverse('group_update', args=(kwargs['pk'],))+'#tab_group_user')


class JoinProjects(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        projects = request.POST.getlist('project')
        roles = request.POST.getlist('role')

        if len(projects) and len(roles):
            for p in projects:
                for r in roles:
                    Project_Group_Role(project_id=p, group_id=group_id, role_id=r).save()

        return HttpResponseRedirect(reverse('group_update', args=(group_id,))+'#tab_group_project')


class QuitProject(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        project_id = kwargs['id']
        Project_Group_Role.objects.filter(project_id=project_id, group_id=group_id).delete()
        return HttpResponseRedirect(reverse('group_update', args=(group_id,))+'#tab_group_project')


class Roles(View):
    def get(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        project_id = kwargs['id']
        data = dict()
        data['all'] = [{'id': n.id, 'name': n.name} for n in get_active_roles()]
        data['selected'] = list(get_group_roles_id(project_id, group_id))
        return HttpResponse(json.dumps(data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        project_id = kwargs['id']

        new = set(map(int, request.POST.getlist('item')))
        old = set(get_group_roles_id(project_id, group_id))
        select = list(new - old)
        unselect = list(old - new)

        for n in select:
            Project_Group_Role(project_id=project_id, group_id=group_id, role_id=n).save()
        Project_Group_Role.objects.filter(project_id=project_id, group_id=group_id, role_id__in=unselect).delete()

        return HttpResponseRedirect(reverse('group_update', args=(group_id,))+'#tab_group_project')
