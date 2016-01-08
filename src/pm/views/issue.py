# coding:utf-8
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Sum
from django.shortcuts import render, redirect
from ..forms import IssueForm, CommentForm, WorktimeForm, WorktimeBlankForm, CommentBlankForm
from ..models import Issue, Comment, Worktime, Project
from ..utils import Helper
import time


_model = Issue
_form = IssueForm
_worktime_form_prefix = 'worktime'
_comment_form_prefix = 'comment'


class Create(CreateView):
    model = _model
    form_class = _form
    template_name = 'project/create_issue.html'

    def get_initial(self):
        initial = super(Create, self).get_initial().copy()
        initial['parent'] = self.request.GET.get('parent', None)
        return initial

    def get_form_kwargs(self):
        kwargs = super(Create, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['project'] = self.kwargs.get('pk')
            data['author'] = self.request.user.id
            kwargs.update({
                'data': data,
            })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Create, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs.get('pk'))
        return context

    def get_success_url(self):
        return self.request.GET.get('redirect', None) or reverse_lazy('issue_list', kwargs={'pk': self.kwargs.get('pk')})


class List(ListView):
    model = _model
    template_name = 'project/issues.html'
    context_object_name = 'issues'

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs.get('pk'))
        return context

    def get_queryset(self):
        return Issue.objects.filter(project__id=self.kwargs.get('pk')).order_by('-updated_on')


class Detail(DetailView):
    model = _model
    template_name = 'project/issue_info.html'
    context_object_name = 'issue'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        context['comments'] = Comment.objects.filter(issue=self.object)
        context['comment_form'] = CommentForm(prefix=_comment_form_prefix)
        context['worktime_form'] = WorktimeForm(prefix=_worktime_form_prefix)
        context['spent_time'] = Worktime.objects.filter(issue=self.object)\
                                    .aggregate(Sum('hours')).get('hours__sum', 0) or 0
        context['form'] = _form(instance=self.object)
        context['subissues'] = Issue.objects.filter(parent=self.object)
        context['watch'] = True if self.request.user in self.object.watchers.all() else False
        return context


class Update(UpdateView):
    model = _model
    form_class = _form
    template_name = 'project/edit_issue.html'

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        context['worktime_form'] = self.worktime_form
        context['comment_form'] = self.comment_form
        return context

    def get_form_kwargs(self):
        kwargs = super(Update, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['author'] = self.request.user.id
            kwargs.update({
                'data': data,
            })
        return kwargs

    def form_valid(self, form):
        self.worktime_form = WorktimeBlankForm(self.request.POST, prefix=_worktime_form_prefix)
        self.comment_form = CommentBlankForm(self.request.POST, prefix=_comment_form_prefix)

        if self.worktime_form.is_valid():
            if self.worktime_form.cleaned_data['hours']:
                self.worktime_form.cleaned_data['issue'] = self.object
                self.worktime_form.cleaned_data['author'] = self.request.user
                self.worktime_form.cleaned_data['date'] = time.strftime("%Y-%m-%d")
                Worktime(**self.worktime_form.cleaned_data).save()
        else:
            return super(Update, self).form_invalid(form)

        if self.comment_form.is_valid():
            if self.comment_form.cleaned_data['content']:
                self.comment_form.cleaned_data['issue'] = self.object
                self.comment_form.cleaned_data['author'] = self.request.user
                Comment(**self.comment_form.cleaned_data).save()
        else:
            return super(Update, self).form_invalid(form)

        return super(Update, self).form_valid(form)

    def form_invalid(self, form):
        self.worktime_form = WorktimeBlankForm(self.request.POST, prefix=_worktime_form_prefix)
        self.comment_form = CommentBlankForm(self.request.POST, prefix=_comment_form_prefix)
        return super(Update, self).form_invalid(form)


class Delete(View):
    def post(self, request, *args, **kwargs):
        issues = Issue.objects.filter(pk=kwargs['pk'])
        project_id = issues[0].project.id
        issues.delete()
        return HttpResponseRedirect(reverse('issue_list', kwargs={'pk': project_id}))


class CommentUpdate(View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        issue_id = Comment.objects.get(pk=pk).issue.id
        comment_form = CommentForm(request.POST, prefix=_comment_form_prefix)

        if comment_form.is_valid():
            Comment.objects.filter(pk=pk).update(**comment_form.cleaned_data)

        return HttpResponseRedirect(reverse('issue_detail', kwargs={'pk':issue_id}))


class Quote(View):
    def get(self, request, *args, **kwargs):
        data = dict()
        comment_id = request.GET.get('comment', None)             # URL?comment=id
        if comment_id is not None:
            comment = Comment.objects.get(pk=comment_id)
            data['content'] = "%s wrote:\n%s" % (comment.author.username, Helper.quote(comment.content))
        else:
            data['content'] = ""
        return JsonResponse(data)


class WorktimeList(ListView):
    model = Worktime
    template_name = 'project/worktimes.html'
    context_object_name = 'worktimes'

    def get_context_data(self, **kwargs):
        context = super(WorktimeList, self).get_context_data(**kwargs)
        issue = Issue.objects.get(pk=self.kwargs.get('pk'))
        context['issue'] = issue
        context['project'] = issue.project
        return context


class WorktimeCreate(CreateView):
    model = Worktime
    form_class = WorktimeForm
    template_name = 'project/create_worktime.html'

    def get_initial(self):
        initial = super(WorktimeCreate, self).get_initial().copy()
        initial['issue'] = self.kwargs.get('pk')
        return initial

    def get_success_url(self):
        if 'continue' in self.request.POST:
            return reverse_lazy('worktime_add', kwargs={'pk': self.kwargs['pk']})
        else:
            return reverse_lazy('worktime_list', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(WorktimeCreate, self).get_context_data(**kwargs)
        issue = Issue.objects.get(pk=self.kwargs.get('pk'))
        context['issue'] = issue
        context['project'] = issue.project
        return context

    def get_form_kwargs(self):
        kwargs = super(WorktimeCreate, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['author'] = self.request.user.id
            kwargs.update({
                'data': data,
            })
        return kwargs


class WorktimeUpdate(UpdateView):
    model = Worktime
    form_class = WorktimeForm
    template_name = 'project/edit_worktime.html'

    def get_success_url(self):
        issue = Worktime.objects.get(pk=self.kwargs.get('pk')).issue
        return reverse_lazy('worktime_list', kwargs={'pk': issue.id})

    def get_context_data(self, **kwargs):
        context = super(WorktimeUpdate, self).get_context_data(**kwargs)
        issue = Worktime.objects.get(pk=self.kwargs.get('pk')).issue
        context['issue'] = issue
        context['project'] = issue.project
        return context


class WorktimeDelete(View):
    def post(self, request, *args, **kwargs):
        query_set = Worktime.objects.filter(pk=kwargs['pk'])
        issue_id = query_set[0].issue.id
        query_set.delete()
        return HttpResponseRedirect(reverse('worktime_list', kwargs={'pk': issue_id}))


class AllIssues(ListView):
    model = _model
    template_name = 'all_issues.html'
    context_object_name = 'issues'


class Watch(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        Issue.watchers.through.objects.get_or_create(user=self.request.user, issue_id=pk)
        return redirect('issue_detail', pk=pk)


class Unwatch(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        Issue.watchers.through.objects.filter(user=self.request.user, issue_id=pk).delete()
        return redirect('issue_detail', pk=pk)


class MyPage(View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context['assigned_issues'] = Issue.objects.filter(assigned_to=self.request.user)
        context['watch_issues'] = [ n.issue for n in Issue.watchers.through.objects.filter(user=self.request.user) ]
        return render(request, 'my_page.html', context)
