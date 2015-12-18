from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from ..forms import GroupForm
from ..models import Project, Project_Groups


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

        context['joined_projects'] = self.object.project_set.all()
        projects = Project.objects.all()
        context['not_joined_projects'] = list(set(projects)-set(context['joined_projects']))
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
        Project_Groups.objects.bulk_create([ Project_Groups(project_id=id, group_id=pk) for id in join_projects ])
        return HttpResponseRedirect(reverse('group_update', args=(pk,))+'#tab_group_project')


class QuitProject(View):
    def post(self, request, *args, **kwargs):
        Project_Groups.objects.filter(project_id=kwargs['id'], group_id=kwargs['pk']).delete()
        return HttpResponseRedirect(reverse('group_update', args=(kwargs['pk'],))+'#tab_group_project')