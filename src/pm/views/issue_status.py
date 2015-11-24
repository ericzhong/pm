from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from ..models import IssueStatus
from ..forms import IssueStatusForm


_model = IssueStatus
_form = IssueStatusForm
_template_dir = 'issue_status'
_name = 'issue_status'
_plural = 'issue_statuses'


class List(ListView):
    model = _model
    template_name = '%s/list.html' % _template_dir
    context_object_name = _plural


class Detail(DetailView):
    model = _model
    template_name = '%s/detail.html' % _template_dir
    context_object_name = _name


class Create(CreateView):
    model = _model
    template_name = '%s/form.html' % _template_dir
    form_class = _form
    success_url = reverse_lazy('%s_list' % _name)


class Update(UpdateView):
    model = _model
    template_name = '%s/form.html' % _template_dir
    form_class = _form

    def get_success_url(self):
        return reverse('%s_detail' % _name, kwargs={'pk': self.object.pk})


class Delete(DeleteView):
    model = _model
    template_name = '%s/confirm_delete.html' % _template_dir
    success_url = reverse_lazy('%s_list' % _name)
