from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect, HttpResponseRedirect, HttpResponse
from ..forms import GroupForm
from ..models import Project, Project_Groups, Role, Group_Project_Role
import json


_model = Group
_form = GroupForm


class List(ListView):
    model = _model
    template_name = '_admin/groups.html'
    context_object_name = 'groups'


class Detail(DetailView):
    model = _model
    template_name = '_admin/groups.html'
    context_object_name = 'group'


class Create(CreateView):
    model = _model
    form_class = _form
    template_name = '_admin/create_group.html'

    def get_success_url(self):
        if 'continue' in self.request.POST:
            return reverse_lazy('group_add')
        else:
            return reverse_lazy('group_list')


class Update(UpdateView):
    model = _model
    form_class = _form
    template_name = '_admin/edit_group.html'
    success_url = reverse_lazy('group_list')

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)

        context['joined_users'] = self.object.user_set.all()
        users = User.objects.all()
        context['not_joined_users'] = list(set(users)-set(context['joined_users']))

        joined_projects = self.object.project_set.all()
        roles = list()
        for p in joined_projects:
            roles.append([ r.role for r in Group_Project_Role.objects.filter(group=self.object, project=p) ])
        context['joined_projects'] = zip(joined_projects, roles)

        projects = Project.objects.all()
        context['not_joined_projects'] = list(set(projects)-set(joined_projects))

        context['roles'] = Role.objects.all()
        return context


class Delete(DeleteView):
    model = _model
    success_url = reverse_lazy('group_list')

    def get(self, request, *args, **kwargs):
        return redirect('group_list')


class AddUsers(View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        add_users = request.POST.getlist('user')
        through = User.groups.through
        through.objects.bulk_create([ through(user_id=id, group_id=pk) for id in add_users ])
        return HttpResponseRedirect(reverse('group_update', args=(pk,))+'#tab_group_user')


class DeleteUser(View):
    def post(self, request, *args, **kwargs):
        User.groups.through.objects.filter(user_id=kwargs['id'], group_id=kwargs['pk']).delete()
        return HttpResponseRedirect(reverse('group_update', args=(kwargs['pk'],))+'#tab_group_user')


class JoinProjects(View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        join_projects = request.POST.getlist('project')
        roles = request.POST.getlist('role')
        if len(join_projects):
            Project_Groups.objects.bulk_create([ Project_Groups(project_id=id, group_id=pk) for id in join_projects ])
            Group_Project_Role.objects.bulk_create(
                    [ Group_Project_Role(project_id=p, group_id=pk, role_id=r) for p in join_projects for r in roles ])
        return HttpResponseRedirect(reverse('group_update', args=(pk,))+'#tab_group_project')


class QuitProject(View):
    def post(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        project_id = kwargs['id']
        Project_Groups.objects.filter(group_id=group_id, project_id=project_id).delete()
        Group_Project_Role.objects.filter(group_id=group_id, project_id=project_id).delete()
        return HttpResponseRedirect(reverse('group_update', args=(kwargs['pk'],))+'#tab_group_project')


class Roles(View):
    def get(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        project_id = kwargs['id']
        data = dict()
        data['all'] = [ {'id':n.id, 'name':n.name} for n in Role.objects.all() ]
        data['selected'] = [ n.role_id for n in Group_Project_Role.objects.filter(group_id=group_id, project_id=project_id) ]
        return HttpResponse(json.dumps(data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        project_id = kwargs['id']
        new = set(map(int, request.POST.getlist('item')))
        old = set([ n.role_id for n in Group_Project_Role.objects.filter(group_id=group_id, project_id=project_id) ])
        select = list(new - old)
        unselect = list(old - new)
        Group_Project_Role.objects.bulk_create( [Group_Project_Role(group_id=group_id, project_id=project_id, role_id=id) for id in select ] )
        Group_Project_Role.objects.filter(group_id=group_id, project_id=project_id, role__pk__in=unselect).delete()
        return HttpResponseRedirect(reverse('group_update', args=(group_id,))+'#tab_group_project')
