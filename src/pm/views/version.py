from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, View
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from ..models import Version, Project, Issue
from ..forms import VersionForm


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


class Create(CreateView):
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


class List(ListView):
    model = _model
    template_name = 'project/settings/versions.html'
    context_object_name = 'versions'

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return context


class Update(UpdateView):
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
        project_id = Version.objects.get(pk=self.kwargs['pk']).project.id
        return _get_back_url(self, project_id=project_id)


class Detail(DetailView):
    model = _model
    template_name = 'project/version_info.html'
    context_object_name = 'version'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        return context


class Delete(View):
    def post(self, request, *args, **kwargs):
        query_set = Version.objects.filter(pk=kwargs['pk'])
        project_id = query_set[0].project.id
        query_set.delete()
        return HttpResponseRedirect(_get_back_url(self, project_id=project_id))


class Roadmap(ListView):
    model = _model
    template_name = 'project/roadmap.html'
    context_object_name = 'versions'

    def get_context_data(self, **kwargs):
        context = super(Roadmap, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return context