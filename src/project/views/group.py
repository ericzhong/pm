from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from ..forms import GroupForm


_model = Group
_form = GroupForm
_template_dir = 'group'
_name = 'group'
_plural = 'groups'


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


class ListUser(View):
    template_name = '%s/user.html' % _template_dir

    def get(self, request, pk):
        users = Group.objects.get(id=pk).user_set.all()
        others = User.objects.exclude(id__in=[ user.id for user in users ])
        group = Group.objects.get(pk=pk)
        return render(request, self.template_name, {'users': users, 'group': group, 'others': others})

    def post(self, request, *args, **kwargs):
        user_ids =  dict(request.POST).get('user_id', None)
        if user_ids is not None:
            pk = kwargs['pk']
            through = User.groups.through
            through.objects.bulk_create([ through(group_id=pk, user_id=id) for id in user_ids ])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DeleteUser(View):

    def get(self, request, pk, id):
        #Group.objects.get(id=pk).user_set.remove(User.objects.get(id=id))
        User.groups.through.objects.get(group__id=pk, user__id=id).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))