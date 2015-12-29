from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect, HttpResponseRedirect, HttpResponse
from ..forms import UserForm
from ..models import Project, Role
import json


_model = User
_form = UserForm


class List(ListView):
    model = _model
    template_name = '_admin/users.html'
    context_object_name = 'users'


class Detail(DetailView):
    model = _model
    template_name = 'user_info.html'
    context_object_name = 'user'


class Create(CreateView):
    model = _model
    form_class = _form
    template_name = '_admin/create_user.html'
    success_url = reverse_lazy('user_list')


class Update(UpdateView):
    model = _model
    template_name = '_admin/edit_user.html'
    form_class = _form
    success_url = reverse_lazy('user_list')

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

        joined_projects = user.project_set.all()
        context['joined_projects'] = zip(joined_projects,
                                         [ n.roles.all() for n in Project.users.through.objects.filter(user=user)])

        projects = Project.objects.all()
        context['not_joined_projects'] = list(set(projects)-set(joined_projects))

        context['joined_groups'] = user.groups.all()
        groups = Group.objects.all()
        context['not_joined_groups'] = list(set(groups)-set(context['joined_groups']))

        context['roles'] = Role.objects.all()
        return context


class Delete(DeleteView):
    model = _model
    success_url = reverse_lazy('user_list')

    def get(self, request, *args, **kwargs):
        return redirect('user_list')


class Lock(View):
    def get(self, request, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        if user.is_active:
            user.is_active = False
            user.save()
        return redirect('user_list')


class Unlock(View):
    def get(self, request, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        if not user.is_active:
            user.is_active = True
            user.save()
        return redirect('user_list')


class JoinProjects(View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        join_projects = request.POST.getlist('project')
        roles = request.POST.getlist('role')
        if len(join_projects):
            for p in join_projects:
                n = Project.users.through(project_id=p, user_id=user_id)
                n.save()
                n.roles.add(*roles)
        return HttpResponseRedirect(reverse('user_update', args=(user_id,))+'#tab_user_project')


class QuitProject(View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        project_id = kwargs['id']
        Project.users.through.objects.filter(user_id=user_id, project_id=project_id).delete()
        return HttpResponseRedirect(reverse('user_update', args=(user_id,))+'#tab_user_project')


class JoinGroups(View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        join_groups = request.POST.getlist('group')
        through = User.groups.through
        through.objects.bulk_create([ through(user_id=pk, group_id=id) for id in join_groups ])
        return HttpResponseRedirect(reverse('user_update', args=(pk,))+'#tab_user_group')


class QuitGroup(View):
    def post(self, request, *args, **kwargs):
        User.groups.through.objects.filter(user_id=kwargs['pk'], group_id=kwargs['id']).delete()
        return HttpResponseRedirect(reverse('user_update', args=(kwargs['pk'],))+'#tab_user_group')


class Roles(View):
    def get(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        project_id = kwargs['id']
        data = dict()
        data['all'] = [ {'id':n.id, 'name':n.name} for n in Role.objects.all() ]
        data['selected'] = [ n.id for n in Project.users.through.objects.get(user_id=user_id,
                                                                             project_id=project_id).roles.all() ]
        return HttpResponse(json.dumps(data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        project_id = kwargs['id']
        new = set(map(int, request.POST.getlist('item')))
        old = set([ n.id for n in Project.users.through.objects.filter(user_id=user_id,
                                                                       project_id=project_id)[0].roles.all() ])
        select = list(new - old)
        unselect = list(old - new)
        n = Project.users.through.objects.get(user_id=user_id, project_id=project_id)
        n.roles.add(*select)
        n.roles.remove(*unselect)
        return HttpResponseRedirect(reverse('user_update', args=(user_id,))+'#tab_user_project')
