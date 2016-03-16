from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, View, ListView
from django.http import HttpResponseRedirect
from ..models import Project, IssueCategory
from ..forms import IssueCategoryForm
from .project import get_other_projects_html
from .auth import PermissionMixin
from .base import CreateSuccessMessageMixin, UpdateSuccessMessageMixin, delete_success_message

_model = IssueCategory
_form = IssueCategoryForm


class Create(PermissionMixin, CreateSuccessMessageMixin, CreateView):
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

    def has_perm(self):
        user = self.request.user
        return user.is_authenticated() and \
            user.has_perm('pm.manage_issue_category', Project.objects.get(pk=self.kwargs.get('pk')))


class List(PermissionMixin, ListView):
    model = _model
    template_name = 'project/settings/issue_categories.html'
    context_object_name = 'issue_categories'

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        project_id = self.kwargs['pk']
        context['project'] = Project.objects.get(pk=project_id)
        context['other_projects'] = get_other_projects_html(project_id)
        context['order'] = self.order
        context['paging'] = {'length': self.length, 'offset': self.offset, 'page_size': self.page_size}
        return context

    def get_queryset(self):
        objects = self.model.objects.filter(project__id=self.kwargs.get('pk')).order_by('id')

        order = self.request.GET.get('order', None)
        from ..utils import Helper
        if order in Helper.get_orderby_options(['name']):
            objects = objects.order_by(order)
            self.order = order
        else:
            self.order = ""

        self.length = len(objects)
        self.offset = Helper.get_offset(self.request.GET.get('offset', None))
        from .settings import page_size
        self.page_size = page_size()

        return objects[self.offset:self.offset+self.page_size]

    def has_perm(self):
        user = self.request.user
        return user.has_perm('pm.manage_issue_category', Project.objects.get(pk=self.kwargs.get('pk')))


class Update(PermissionMixin, UpdateSuccessMessageMixin, UpdateView):
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

    def has_perm(self):
        user = self.request.user
        return user.has_perm('pm.manage_issue_category', IssueCategory.objects.get(pk=self.kwargs.get('pk')).project)


class Delete(PermissionMixin, View):
    def post(self, request, *args, **kwargs):
        query_set = IssueCategory.objects.filter(pk=kwargs['pk'])
        name = str(query_set[0])
        project_id = query_set[0].project.id
        query_set.delete()

        from django.contrib import messages
        messages.success(self.request, delete_success_message % name)

        return HttpResponseRedirect(reverse('issue_category_list', kwargs={'pk': project_id}))

    def has_perm(self):
        user = self.request.user
        return user.has_perm('pm.manage_issue_category', IssueCategory.objects.get(pk=self.kwargs.get('pk')).project)
