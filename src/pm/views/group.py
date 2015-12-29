from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect, HttpResponseRedirect, HttpResponse
from ..forms import GroupForm
from ..models import Project, Role
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
        group = self.object

        context['joined_users'] = group.user_set.all()
        users = User.objects.all()
        context['not_joined_users'] = list(set(users)-set(context['joined_users']))

        joined_projects = group.project_set.all()
        context['joined_projects'] = zip(joined_projects,
                                         [ n.roles.all() for n in Project.groups.through.objects.filter(group=group)])

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
        group_id = kwargs['pk']
        join_projects = request.POST.getlist('project')
        roles = request.POST.getlist('role')
        if len(join_projects):
            for p in join_projects:
                n = Project.groups.through(project_id=p, group_id=group_id)
                n.save()
                n.roles.add(*roles)
        return HttpResponseRedirect(reverse('group_update', args=(group_id,))+'#tab_group_project')


class QuitProject(View):
    def post(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        project_id = kwargs['id']
        Project.groups.through.objects.filter(group_id=group_id, project_id=project_id).delete()
        return HttpResponseRedirect(reverse('group_update', args=(group_id,))+'#tab_group_project')


class Roles(View):
    def get(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        project_id = kwargs['id']
        data = dict()
        data['all'] = [ {'id':n.id, 'name':n.name} for n in Role.objects.all() ]
        data['selected'] = [ n.id for n in
                             Project.groups.through.objects.get(group_id=group_id, project_id=project_id).roles.all() ]
        return HttpResponse(json.dumps(data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        project_id = kwargs['id']
        new = set(map(int, request.POST.getlist('item')))
        old = set([ n.id for n in
                    Project.groups.through.objects.filter(group_id=group_id, project_id=project_id)[0].roles.all() ])
        select = list(new - old)
        unselect = list(old - new)
        n = Project.groups.through.objects.get(group_id=group_id, project_id=project_id)
        n.roles.add(*select)
        n.roles.remove(*unselect)
        return HttpResponseRedirect(reverse('group_update', args=(group_id,))+'#tab_group_project')
