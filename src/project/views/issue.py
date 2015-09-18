from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from ..forms import IssueForm
from ..models import Issue


_model = Issue
_form = IssueForm
_template_dir = 'issue'
_name = 'issue'
_plural = 'issues'


class List(ListView):
    model = _model
    template_name = '%s/list.html' % _template_dir
    context_object_name = _plural


class Detail(DetailView):
    model = _model
    template_name = '%s/detail.html' % _template_dir
    context_object_name = _name

    def get_object(self):
        object = super(Detail, self).get_object()
        if object.start_date is not None:
            object.start_date = object.start_date.strftime('%Y-%m-%d')
        if object.due_date is not None:
            object.due_date = object.due_date.strftime('%Y-%m-%d')
        return object


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