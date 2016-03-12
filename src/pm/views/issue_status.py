from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, HttpResponseRedirect
from ..models import IssueStatus
from ..forms import IssueStatusForm
from .base import CreateSuccessMessageMixin, UpdateSuccessMessageMixin, DeleteSuccessMessageMixin
from .auth import SuperuserRequiredMixin

_model = IssueStatus
_form = IssueStatusForm


class List(SuperuserRequiredMixin, ListView):
    model = _model
    template_name = '_admin/issue_statuses.html'
    context_object_name = 'issue_statuses'


class Create(SuperuserRequiredMixin, CreateSuccessMessageMixin, CreateView):
    model = _model
    template_name = '_admin/create_issue_status.html'
    form_class = _form
    success_message = "OK"

    def get_success_url(self):
        if self.request.POST.get('continue', None) is None:
            return reverse_lazy('issue_status_list')
        else:
            return reverse_lazy('issue_status_add')


class Update(SuperuserRequiredMixin, UpdateSuccessMessageMixin, UpdateView):
    model = _model
    template_name = '_admin/edit_issue_status.html'
    form_class = _form

    def get_success_url(self):
        return reverse_lazy('issue_status_update', kwargs={'pk': self.object.id})


class Delete(SuperuserRequiredMixin, DeleteSuccessMessageMixin, DeleteView):
    model = _model
    success_url = reverse_lazy('issue_status_list')

    def get(self, request, *args, **kwargs):
        return redirect('issue_status_list')

    def delete(self, request, *args, **kwargs):
        if int(self.kwargs['pk']) in IssueStatus.UNDELETABLE:
            return HttpResponseRedirect(self.success_url)
        else:
            return super(Delete, self).delete(request, *args, **kwargs)
