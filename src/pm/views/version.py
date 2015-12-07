from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, View
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from ..models import Version, Project
from ..forms import VersionForm


_model = Version
_form = VersionForm


class Create(CreateView):
    model = _model
    form_class = _form
    template_name = 'project/create_version.html'

    def get_context_data(self, **kwargs):
        context = super(Create, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
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
        backurl = self.request.GET.get('backurl', None)
        if backurl is None:
            return reverse_lazy('version_roadmap', kwargs={'pk': self.kwargs.get('pk')})
        else:
            return reverse_lazy('version_list', kwargs={'pk': self.kwargs.get('pk')})


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
        context['project'] = Version.objects.get(pk=self.kwargs['pk']).project
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
        backurl = self.request.GET.get('backurl', None)
        if backurl is None:
            return reverse_lazy('version_detail', kwargs={'pk': self.kwargs.get('pk')})
        else:
            versions = Version.objects.filter(pk=self.kwargs['pk'])
            project_id = versions[0].project.id
            return reverse_lazy('version_list', kwargs={'pk': project_id})


class Detail(DetailView):
    model = _model
    template_name = 'project/version_info.html'
    context_object_name = 'version'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['project'] = Version.objects.get(pk=self.kwargs['pk']).project
        return context


class Delete(View):
    def post(self, request, *args, **kwargs):
        versions = Version.objects.filter(pk=kwargs['pk'])
        project_id = versions[0].project.id
        versions.delete()

        backurl = request.GET.get('backurl', None)
        if backurl is None:
            return HttpResponseRedirect(reverse('version_roadmap', kwargs={'pk': project_id}))
        else:
            return HttpResponseRedirect(reverse('version_list', kwargs={'pk': project_id}))


class Roadmap(ListView):
    model = _model
    template_name = 'project/roadmap.html'
    context_object_name = 'versions'

    def get_context_data(self, **kwargs):
        context = super(Roadmap, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return context