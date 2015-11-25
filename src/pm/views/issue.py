# coding:utf-8
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.db.models import Sum
from ..forms import IssueForm, CommentForm, WorktimeForm
from ..models import Issue, Comment, Worktime, Project
from ..utils import Helper
import time


_model = Issue
_form = IssueForm
_template_dir = ''
_name = ''


class Create(CreateView):
    model = _model
    template_name = 'project/create_issue.html'
    form_class = _form

    def get_context_data(self, **kwargs):
        context = super(Create, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs.get('pk'))
        return context

    def get_success_url(self):
        return reverse_lazy('issue_list', kwargs={'pk': self.kwargs.get('pk')})


class List(ListView):
    model = _model
    template_name = 'project/issues.html'
    context_object_name = 'issues'


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

    def get_context_data(self, *args, **kwargs):
        context = super(Detail, self).get_context_data()
        context['comments'] = Comment.objects.filter(issue=context['object'])
        context['comment'] = CommentForm()
        context['spent_time'] = Worktime.objects.filter(issue=kwargs['object'])\
                                    .aggregate(Sum('hours')).get('hours__sum', 0) or 0
        return context





class Update(View):
    template_name = '%s/update.html' % _template_dir

    def get(self, request, **kwargs):
        issue = Issue.objects.get(pk=kwargs['pk'])
        issue_form = IssueForm(prefix='issue', instance=issue)

        comment_id = request.GET.get('quote', None)     # url?quote=comment_id
        comment = None
        if comment_id is not None:
            comment = Comment.objects.get(id=comment_id)
            comment.content = "%s:\n%s" % (comment.author.username, Helper.quote(comment.content))
        comment_form = CommentForm(instance=comment, prefix='comment')
        worktime_form = WorktimeForm(prefix='worktime')
        return render(request, self.template_name, {'form': issue_form, 'comment': comment_form, 'worktime': worktime_form})

    def post(self, request, **kwargs):
        pk = kwargs['pk']
        issue_form = IssueForm(request.POST, prefix='issue')
        comment_form = CommentForm(request.POST, prefix='comment')
        worktime_form = WorktimeForm(request.POST, prefix='worktime')

        if issue_form.is_valid():
            Issue.objects.filter(pk=pk).update(**issue_form.cleaned_data)

            if comment_form.is_valid():
                comment_form.cleaned_data['issue_id'] = pk
                comment_form.cleaned_data['author_id'] = request.user.id
                Comment(**comment_form.cleaned_data).save()

            if worktime_form.is_valid():
                worktime_form.cleaned_data['project_id'] = Issue.objects.get(pk=pk).project_id
                worktime_form.cleaned_data['issue_id'] = pk
                worktime_form.cleaned_data['author_id'] = request.user.id
                worktime_form.cleaned_data['date'] = time.strftime("%Y-%m-%d")
                Worktime(**worktime_form.cleaned_data).save()
            return HttpResponseRedirect(reverse('%s_detail' % _name, kwargs={'pk': pk}))
        else:
            return render(request, self.template_name, {'form': issue_form, 'comment': comment_form})


class Delete(DeleteView):
    model = _model
    template_name = '%s/confirm_delete.html' % _template_dir
    success_url = reverse_lazy('%s_list' % _name)


class CommentUpdate(View):
    def post(self, request, **kwargs):
        pk = kwargs['pk']
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            Comment.objects.filter(pk=pk).update(**comment_form.cleaned_data)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CommentDelete(View):
    def get(self, request, **kwargs):
        pk = kwargs['pk']
        Comment.objects.get(id=pk).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))