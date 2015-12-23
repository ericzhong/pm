from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect, HttpResponseRedirect
from ..forms import UserForm
from ..models import Project, Member, Role, User_Project_Role


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

        context['joined_projects'] = [ m.project for m in Member.objects.filter(user=self.object) ]
        projects = Project.objects.all()
        context['not_joined_projects'] = list(set(projects)-set(context['joined_projects']))

        context['joined_groups'] = self.object.groups.all()
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
        pk = kwargs['pk']
        join_projects = request.POST.getlist('project')
        roles = request.POST.getlist('role')
        if len(join_projects):
            Member.objects.bulk_create([ Member(project_id=id, user_id=pk) for id in join_projects ])
            User_Project_Role.objects.bulk_create(
                [ User_Project_Role(project_id=p, user_id=pk, role_id=r) for p in join_projects for r in roles ])
        return HttpResponseRedirect(reverse('user_update', args=(pk,))+'#tab_user_project')


class QuitProject(View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        project_id = kwargs['id']
        Member.objects.filter(user_id=user_id, project_id=project_id).delete()
        User_Project_Role.objects.filter(user_id=user_id, project_id=project_id).delete()
        return HttpResponseRedirect(reverse('user_update', args=(kwargs['pk'],))+'#tab_user_project')


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