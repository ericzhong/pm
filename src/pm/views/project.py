from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from ..models import Project, Member, Issue
from ..forms import ProjectForm


_model = Project
_form = ProjectForm
_template_dir = 'project'



class List(ListView):
    model = _model
    template_name = 'project_list.html'
    context_object_name = 'projects'


class Detail(DetailView):
    model = _model
    template_name = '%s/overview.html' % _template_dir
    context_object_name = 'project'

    '''
    def get_object(self):
        object = super(Detail, self).get_object()
        object.created_on = object.created_on.strftime('%Y-%m-%d %H:%M:%S')
        object.updated_on = object.updated_on.strftime('%Y-%m-%d %H:%M:%S')
        object.members = Member.objects.filter(project=object)
        return object
    '''


class Create(CreateView):
    model = _model
    template_name = 'create_project.html'
    form_class = _form
    success_url = reverse_lazy('project_list')

    def get_initial(self):
        initial = super(Create, self).get_initial()
        initial = initial.copy()
        initial['parent'] = self.request.GET.get('parent', None)
        return initial


class Update(UpdateView):
    model = _model
    template_name = '%s/settings/info.html' % _template_dir
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


class Issues(View):
    template_name = '%s/issues.html' % _template_dir

    def get(self, request, **kwargs):
        issues = Issue.objects.filter(project__id=kwargs['pk'])
        print issues
        return render(request, self.template_name, {'issues': issues})


class ListMember(View):
    template_name = '%s/member.html' % _template_dir

    def get(self, request, pk):
        objects = Member.objects.filter(project__id=pk)
        users = [ object.user for object in objects ]
        others = User.objects.exclude(id__in=[ user.id for user in users ])
        project = Project.objects.get(pk=pk)
        return render(request, self.template_name, {'users': users, 'project': project, 'others': others})

    def post(self, request, *args, **kwargs):
        user_ids =  dict(request.POST).get('user_id', None)
        if user_ids is not None:
            pk = kwargs['pk']
            Member.objects.bulk_create([ Member(project_id=pk, user_id=id) for id in user_ids ])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DeleteMember(View):

    def get(self, request, pk, id):
        Member.objects.get(project__id=pk, user__id=id).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
