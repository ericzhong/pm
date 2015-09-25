from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from ..models import Project, Member
from ..forms import ProjectForm


_model = Project
_form = ProjectForm
_template_dir = 'project'
_name = 'project'
_plural = 'projects'




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
        object.created_on = object.created_on.strftime('%Y-%m-%d %H:%M:%S')
        object.updated_on = object.updated_on.strftime('%Y-%m-%d %H:%M:%S')
        object.members = Member.objects.filter(project=object)
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



class ListMember(View):
    template_name = '%s/member.html' % _template_dir

    def get(self, request, pk):
        objects = Member.objects.filter(project__id=pk)
        users = [ object.user for object in objects ]
        others = User.objects.exclude(id__in=[ user.id for user in users ])
        project = Project.objects.get(pk=pk)
        return render(request, self.template_name, {'users': users, 'project': project, 'others': others})

    def post(self, request, *args, **kwargs):
        user_ids =  dict(request.POST).get('user_id', None)
        if user_ids is not None:
            pk = kwargs['pk']
            Member.objects.bulk_create([ Member(project_id=pk, user_id=id) for id in user_ids ])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DeleteMember(View):

    def get(self, request, pk, id):
        Member.objects.get(project__id=pk, user__id=id).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))