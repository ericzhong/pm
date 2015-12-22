from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from ..models import Role
from ..forms import RoleForm


_model = Role
_form = RoleForm


class List(ListView):
    model = _model
    template_name = '_admin/roles.html'
    context_object_name = 'roles'


class Create(CreateView):
    model = _model
    form_class = _form
    template_name = '_admin/create_role.html'

    def get_success_url(self):
        if 'continue' in self.request.POST:
            return reverse_lazy('role_add')
        else:
            return reverse_lazy('role_list')


class Update(UpdateView):
    model = _model
    form_class = _form
    template_name = '_admin/edit_role.html'
    success_url = reverse_lazy('role_list')


class Delete(DeleteView):
    model = _model
    success_url = reverse_lazy('role_list')

    def get(self, request, *args, **kwargs):
        return redirect('role_list')
