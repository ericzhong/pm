from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from ..models import IssueTag
from ..forms import IssueTagForm
from .base import CreateSuccessMessageMixin, UpdateSuccessMessageMixin, DeleteSuccessMessageMixin


_model = IssueTag
_form = IssueTagForm


class List(ListView):
    model = _model
    template_name = '_admin/issue_tags.html'
    context_object_name = 'issue_tags'


class Create(CreateSuccessMessageMixin, CreateView):
    model = _model
    template_name = '_admin/create_issue_tag.html'
    form_class = _form

    def get_success_url(self):
        if self.request.POST.get('continue', None) is None:
            return reverse_lazy('issue_tag_list')
        else:
            return reverse_lazy('issue_tag_add')


class Update(UpdateSuccessMessageMixin, UpdateView):
    model = _model
    template_name = '_admin/edit_issue_tag.html'
    form_class = _form

    def get_success_url(self):
        return reverse_lazy('issue_tag_update', kwargs={'pk': self.object.id})


class Delete(DeleteSuccessMessageMixin, DeleteView):
    model = _model
    success_url = reverse_lazy('issue_tag_list')

    def get(self, request, *args, **kwargs):
        return redirect('issue_tag_list')
