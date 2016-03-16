from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, HttpResponseRedirect
from ..models import IssueTag
from ..forms import IssueTagForm
from .base import CreateSuccessMessageMixin, UpdateSuccessMessageMixin, DeleteSuccessMessageMixin
from .auth import SuperuserRequiredMixin

_model = IssueTag
_form = IssueTagForm


class List(SuperuserRequiredMixin, ListView):
    model = _model
    template_name = '_admin/issue_tags.html'
    context_object_name = 'issue_tags'

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        context['order'] = self.order
        context['paging'] = {'length': self.length, 'offset': self.offset, 'page_size': self.page_size}
        return context

    def get_queryset(self):
        objects = self.model.objects.all().order_by("id")

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


class Create(SuperuserRequiredMixin, CreateSuccessMessageMixin, CreateView):
    model = _model
    template_name = '_admin/create_issue_tag.html'
    form_class = _form

    def get_success_url(self):
        if self.request.POST.get('continue', None) is None:
            return reverse_lazy('issue_tag_list')
        else:
            return reverse_lazy('issue_tag_add')


class Update(SuperuserRequiredMixin, UpdateSuccessMessageMixin, UpdateView):
    model = _model
    template_name = '_admin/edit_issue_tag.html'
    form_class = _form

    def get_success_url(self):
        return reverse_lazy('issue_tag_update', kwargs={'pk': self.object.id})


class Delete(SuperuserRequiredMixin, DeleteSuccessMessageMixin, DeleteView):
    model = _model
    success_url = reverse_lazy('issue_tag_list')

    def get(self, request, *args, **kwargs):
        return redirect('issue_tag_list')

    def delete(self, request, *args, **kwargs):
        if int(self.kwargs['pk']) in IssueTag.UNDELETABLE:
            return HttpResponseRedirect(self.success_url)
        else:
            return super(Delete, self).delete(request, *args, **kwargs)
