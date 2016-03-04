from django.views.generic import ListView, DetailView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from ..models import Version, Project
from ..forms import VersionForm
from .project import get_other_projects_html
from .auth import PermCheckCreateView, PermCheckUpdateView, PermCheckListView, PermCheckView
from .base import CreateSuccessMessageMixin, UpdateSuccessMessageMixin, delete_success_message, decorate_object

_model = Version
_form = VersionForm


def _get_back_url(view, version_id=None, project_id=None):
    backurl = view.request.GET.get('backurl', None)
    if backurl is not None:
        return reverse_lazy('version_list', kwargs={'pk': project_id})
    else:
        if version_id is not None:
            return reverse_lazy('version_detail', kwargs={'pk': version_id})
        else:
            return reverse_lazy('version_roadmap', kwargs={'pk': project_id})


class Create(CreateSuccessMessageMixin, PermCheckCreateView):
    model = _model
    form_class = _form
    template_name = 'project/create_version.html'

    def get_context_data(self, **kwargs):
        context = super(Create, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['project'] = Project.objects.get(pk=pk)
        context['backurl'] = _get_back_url(self, project_id=pk)
        return context

    def get_form_kwargs(self):
        kwargs = super(Create, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['project'] = self.kwargs.get('pk')
            kwargs.update({
                'data': data,
            })
        return kwargs

    def get_success_url(self):
        return _get_back_url(self, project_id=self.kwargs['pk'])

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.manage_version', Project.objects.get(pk=self.kwargs.get('pk')))


class List(PermCheckListView):
    model = _model
    template_name = 'project/settings/versions.html'
    context_object_name = 'versions'

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        project_id = self.kwargs['pk']
        context['project'] = Project.objects.get(pk=project_id)
        context['other_projects'] = get_other_projects_html(project_id)
        return context

    def get_queryset(self):
        return Version.objects.filter(project__id=self.kwargs.get('pk')).order_by('id')

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.manage_version', Project.objects.get(pk=self.kwargs.get('pk')))


class Update(UpdateSuccessMessageMixin, PermCheckUpdateView):
    model = _model
    form_class = _form
    template_name = 'project/edit_version.html'

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        version = context['object']
        context['project'] = version.project
        context['backurl'] = _get_back_url(self, version_id=version.id, project_id=version.project.id)
        return context

    def get_form_kwargs(self):
        kwargs = super(Update, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['project'] = Version.objects.get(pk=self.kwargs['pk']).project.id
            kwargs.update({
                'data': data,
            })
        return kwargs

    def get_success_url(self):
        version_id = self.kwargs['pk']
        project_id = Version.objects.get(pk=version_id).project.id
        return _get_back_url(self, version_id=version_id, project_id=project_id)

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.manage_version', Version.objects.get(pk=self.kwargs['pk']).project)


class Detail(DetailView):
    model = _model
    template_name = 'project/version_info.html'
    context_object_name = 'version'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        context['other_projects'] = get_other_projects_html(self.object.project.id)
        from ..models import IssueStatus
        context['IssueStatus'] = IssueStatus
        return context


class Delete(PermCheckView):
    def post(self, request, *args, **kwargs):
        query_set = Version.objects.filter(pk=kwargs['pk'])
        project_id = query_set[0].project.id

        from django.contrib import messages
        messages.success(self.request, delete_success_message % decorate_object(query_set[0]))

        query_set.delete()
        return HttpResponseRedirect(_get_back_url(self, project_id=project_id))

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.manage_version', Version.objects.get(pk=self.kwargs['pk']).project)


class Roadmap(ListView):
    model = _model
    template_name = 'project/roadmap.html'
    context_object_name = 'versions'

    def get_context_data(self, **kwargs):
        context = super(Roadmap, self).get_context_data(**kwargs)
        project_id = self.kwargs['pk']
        context['project'] = Project.objects.get(pk=project_id)
        context['other_projects'] = get_other_projects_html(project_id)
        from ..models import IssueStatus
        context['IssueStatus'] = IssueStatus
        return context