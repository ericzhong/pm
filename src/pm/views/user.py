from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.shortcuts import redirect
from ..forms import UserForm


_model = User
_form = UserForm


class List(ListView):
    model = _model
    template_name = '_admin/users.html'
    context_object_name = 'users'


class Detail(DetailView):
    model = _model
    template_name = 'user_info.html'
    context_object_name = 'user'


class Create(CreateView):
    model = _model
    form_class = _form
    template_name = '_admin/create_user.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        self.object = form.save()
        self.object.set_password(form.cleaned_data['password1'])
        return super(Create, self).form_valid(form)


class Update(UpdateView):
    model = _model
    template_name = '_admin/edit_user.html'
    form_class = _form
    success_url = reverse_lazy('user_list')


class Delete(DeleteView):
    model = _model
    success_url = reverse_lazy('user_list')

    def get(self, request, *args, **kwargs):
        return redirect('user_list')


class Lock(View):
    def get(self, request, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        if user.is_active:
            user.is_active = False
            user.save()
        return redirect('user_list')


class Unlock(View):
    def get(self, request, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        if not user.is_active:
            user.is_active = True
            user.save()
        return redirect('user_list')