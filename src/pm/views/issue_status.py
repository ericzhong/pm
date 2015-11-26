from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from ..models import IssueStatus
from ..forms import IssueStatusForm


_model = IssueStatus
_form = IssueStatusForm


class List(ListView):
    model = _model
    template_name = '_admin/issue_statuses.html'
    context_object_name = 'issue_statuses'


class Create(CreateView):
    model = _model
    template_name = '_admin/create_issue_status.html'
    form_class = _form

    def get_success_url(self):
        if self.request.POST.get('continue', None) is None:
            return reverse_lazy('issue_status_list')
        else:
            return reverse_lazy('issue_status_add')


class Update(UpdateView):
    model = _model
    template_name = '_admin/edit_issue_status.html'
    form_class = _form
    success_url = reverse_lazy('issue_status_list')


class Delete(DeleteView):
    model = _model
    success_url = reverse_lazy('issue_status_list')

    def get(self, request, *args, **kwargs):
        return redirect('issue_status_list')
