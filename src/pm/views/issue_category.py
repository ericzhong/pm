from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, View
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from ..models import Project, IssueCategory
from ..forms import IssueCategoryForm
from .project import get_other_projects_html

_model = IssueCategory
_form = IssueCategoryForm


class Create(CreateView):
    model = _model
    form_class = _form
    template_name = 'project/create_issue_category.html'

    def get_context_data(self, **kwargs):
        context = super(Create, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['project'] = Project.objects.get(pk=pk)
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
        if 'continue' in self.request.POST:
            return reverse_lazy('issue_category_add', kwargs={'pk': self.kwargs['pk']})
        else:
            return reverse_lazy('issue_category_list', kwargs={'pk': self.kwargs['pk']})


class List(ListView):
    model = _model
    template_name = 'project/settings/issue_categories.html'
    context_object_name = 'issue_categories'

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        project_id = self.kwargs['pk']
        context['project'] = Project.objects.get(pk=project_id)
        context['other_projects'] = get_other_projects_html(project_id)
        return context


class Update(UpdateView):
    model = _model
    form_class = _form
    template_name = 'project/edit_issue_category.html'

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        context['project'] = context['object'].project
        return context

    def get_form_kwargs(self):
        kwargs = super(Update, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['project'] = IssueCategory.objects.get(pk=self.kwargs['pk']).project.id
            kwargs.update({
                'data': data,
            })
        return kwargs

    def get_success_url(self):
        project_id = IssueCategory.objects.get(pk=self.kwargs['pk']).project.id
        return reverse_lazy('issue_category_list', kwargs={'pk': project_id})


class Delete(View):
    def post(self, request, *args, **kwargs):
        query_set = IssueCategory.objects.filter(pk=kwargs['pk'])
        project_id = query_set[0].project.id
        query_set.delete()
        return HttpResponseRedirect(reverse('issue_category_list', kwargs={'pk': project_id}))
