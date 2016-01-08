from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, HttpResponse
from ..models import Project, Issue, Role
from ..forms import ProjectForm
import json


_model = Project
_form = ProjectForm


class List(ListView):
    model = _model
    template_name = 'project_list.html'
    context_object_name = 'projects'


class Detail(DetailView):
    model = _model
    template_name = 'project/overview.html'
    context_object_name = 'project'


class Create(CreateView):
    model = _model
    template_name = 'create_project.html'
    form_class = _form
    success_url = reverse_lazy('project_list')

    def get_initial(self):
        initial = super(Create, self).get_initial().copy()
        initial['parent'] = self.request.GET.get('parent', None)
        return initial


class Update(UpdateView):
    model = _model
    template_name = 'project/settings/info.html'
    form_class = _form

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
        context = dict()
        project = Project.objects.get(id=project_id)
        context['project'] = project

        joined_users = project.users.all()
        context['joined_users'] = zip(joined_users,
            [ Project.users.through.objects.get(project_id=project_id, user=n).roles.all() for n in joined_users ])

        users = User.objects.all()
        context['not_joined_users'] = list(set(users)-set(joined_users))

        joined_groups = project.groups.all()
        context['joined_groups'] = zip(joined_groups,
            [ Project.groups.through.objects.get(project_id=project_id, group=n).roles.all() for n in joined_groups ])

        groups = Group.objects.all()
        context['not_joined_groups'] = list(set(groups)-set(joined_groups))

        context['roles'] = Role.objects.all()
        return render(request, self.template_name, context)


class DeleteMember(View):
    def post(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        if 'user_id' in request.GET:
            Project.users.through.objects.filter(user_id=request.GET['user_id'], project_id=project_id).delete()
        elif 'group_id' in request.GET:
            Project.groups.through.objects.filter(group_id=request.GET['group_id'], project_id=project_id).delete()
        return redirect('member_list', pk=project_id)


class UpdateMember(View):
    def post(self, request, *args, **kwargs):
        user_ids =  dict(request.POST).get('user_id', None)
        if user_ids is not None:
            pk = kwargs['pk']
            Member.objects.bulk_create([ Member(project_id=pk, user_id=id) for id in user_ids ])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CreateMember(View):
    def post(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        users = request.POST.getlist('user')
        groups = request.POST.getlist('group')
        roles = request.POST.getlist('role')
        for id in users:
            n = Project.users.through(project_id=project_id, user_id=id)
            n.save()
            n.roles.add(*roles)

        for id in groups:
            n = Project.groups.through(project_id=project_id, group_id=id)
            n.save()
            n.roles.add(*roles)
        return redirect('member_list', pk=project_id)


class MemberRoles(View):
    def get(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        data = dict()
        data['all'] = [ {'id':n.id, 'name':n.name} for n in Role.objects.all() ]

        if 'user_id' in request.GET:
            data['selected'] = [ n.id for n in
                 Project.users.through.objects.get(user_id=request.GET['user_id'], project_id=project_id).roles.all() ]
        elif 'group_id' in request.GET:
            data['selected'] = [ n.id for n in
                Project.groups.through.objects.get(group_id=request.GET['group_id'], project_id=project_id).roles.all() ]
        return HttpResponse(json.dumps(data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        new = set(map(int, request.POST.getlist('item')))

        if 'user_id' in request.GET:
            obj = Project.users.through.objects.get(user_id=request.GET['user_id'], project_id=project_id)
        elif 'group_id' in request.GET:
            obj = Project.groups.through.objects.get(group_id=request.GET['group_id'], project_id=project_id)
        else:
            return redirect('member_list', pk=project_id)

        old = set([ n.id for n in obj.roles.all() ])
        select = list(new - old)
        unselect = list(old - new)
        obj.roles.add(*select)
        obj.roles.remove(*unselect)
        return redirect('member_list', pk=project_id)