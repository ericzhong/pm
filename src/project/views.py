from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from .models import Project, Issue, IssueStatus, IssueType, Version
from .forms import ProjectForm, IssueForm, IssueTypeForm, IssueStatusForm, VersionForm


class ProjectList(ListView):
    model = Project
    template_name = 'project/list.html'
    context_object_name = 'projects'


class ProjectDetail(DetailView):
    model = Project
    template_name = 'project/detail.html'
    context_object_name = 'project'

    def get_object(self):
        object = super(ProjectDetail, self).get_object()
        object.created_on = object.created_on.strftime('%Y-%m-%d %H:%M:%S')
        object.updated_on = object.updated_on.strftime('%Y-%m-%d %H:%M:%S')
        return object


class ProjectCreate(CreateView):
    model = Project
    template_name = 'project/form.html'
    form_class = ProjectForm
    success_url = reverse_lazy('project_list')


class ProjectUpdate(UpdateView):
    model = Project
    template_name = 'project/form.html'
    form_class = ProjectForm

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})


class ProjectDelete(DeleteView):
    model = Project
    template_name = 'project/confirm_delete.html'
    success_url = reverse_lazy('project_list')



class IssueList(ListView):
    model = Issue
    template_name = 'issue/list.html'
    context_object_name = 'issues'


class IssueDetail(DetailView):
    model = Issue
    template_name = 'issue/detail.html'
    context_object_name = 'issue'

    def get_object(self):
        object = super(IssueDetail, self).get_object()
        object.start_date = object.start_date.strftime('%Y-%m-%d')
        object.due_date = object.due_date.strftime('%Y-%m-%d')
        return object


class IssueCreate(CreateView):
    model = Issue
    template_name = 'issue/form.html'
    form_class = IssueForm
    success_url = reverse_lazy('issue_list')


class IssueUpdate(UpdateView):
    model = Issue
    template_name = 'issue/form.html'
    form_class = IssueForm

    def get_success_url(self):
        return reverse('issue_detail', kwargs={'pk': self.object.pk})


class IssueDelete(DeleteView):
    model = Issue
    template_name = 'issue/confirm_delete.html'
    success_url = reverse_lazy('issue_list')




class IssueTypeList(ListView):
    model = IssueType
    template_name = 'issue_type/list.html'
    context_object_name = 'issue_types'


class IssueTypeDetail(DetailView):
    model = IssueType
    template_name = 'issue_type/detail.html'
    context_object_name = 'issue_type'


class IssueTypeCreate(CreateView):
    model = IssueType
    template_name = 'issue_type/form.html'
    form_class = IssueTypeForm
    success_url = reverse_lazy('issue_type_list')


class IssueTypeUpdate(UpdateView):
    model = IssueType
    template_name = 'issue_type/form.html'
    form_class = IssueTypeForm

    def get_success_url(self):
        return reverse('issue_type_detail', kwargs={'pk': self.object.pk})


class IssueTypeDelete(DeleteView):
    model = IssueType
    template_name = 'issue_type/confirm_delete.html'
    success_url = reverse_lazy('issue_type_list')





class IssueStatusList(ListView):
    model = IssueStatus
    template_name = 'issue_status/list.html'
    context_object_name = 'issue_statuses'


class IssueStatusDetail(DetailView):
    model = IssueStatus
    template_name = 'issue_status/detail.html'
    context_object_name = 'issue_status'


class IssueStatusCreate(CreateView):
    model = IssueStatus
    template_name = 'issue_status/form.html'
    form_class = IssueStatusForm
    success_url = reverse_lazy('issue_status_list')


class IssueStatusUpdate(UpdateView):
    model = IssueStatus
    template_name = 'issue_status/form.html'
    form_class = IssueStatusForm

    def get_success_url(self):
        return reverse('issue_status_detail', kwargs={'pk': self.object.pk})


class IssueStatusDelete(DeleteView):
    model = IssueStatus
    template_name = 'issue_status/confirm_delete.html'
    success_url = reverse_lazy('issue_status_list')





class VersionList(ListView):
    model = Version
    template_name = 'version/list.html'
    context_object_name = 'versions'


class VersionDetail(DetailView):
    model = Version
    template_name = 'version/detail.html'
    context_object_name = 'version'

    def get_object(self):
        object = super(VersionDetail, self).get_object()
        object.created_on = object.created_on.strftime('%Y-%m-%d %H:%M:%S')
        object.updated_on = object.updated_on.strftime('%Y-%m-%d %H:%M:%S')
        object.effective_date = object.effective_date.strftime('%Y-%m-%d')
        return object


class VersionCreate(CreateView):
    model = Version
    template_name = 'version/form.html'
    form_class = VersionForm
    success_url = reverse_lazy('version_list')


class VersionUpdate(UpdateView):
    model = Version
    template_name = 'version/form.html'
    form_class = VersionForm

    def get_success_url(self):
        return reverse('version_detail', kwargs={'pk': self.object.pk})


class VersionDelete(DeleteView):
    model = Version
    template_name = 'version/confirm_delete.html'
    success_url = reverse_lazy('version_list')

