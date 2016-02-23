# coding:utf-8
from django.views.generic import ListView, View
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Sum
from django.shortcuts import render, redirect
from ..forms import IssueForm, CommentForm, WorktimeForm, WorktimeBlankForm, CommentBlankForm
from ..models import Issue, Comment, Worktime, Project, Version
from ..utils import Helper
from .project import get_other_projects_html
from .auth import PermCheckView, PermCheckUpdateView, PermCheckListView, \
    PermCheckCreateView, PermCheckDetailView
from .base import CreateSuccessMessageMixin, update_success_message, delete_success_message
import time


_model = Issue
_form = IssueForm
_worktime_form_prefix = 'worktime'
_comment_form_prefix = 'comment'


class Create(CreateSuccessMessageMixin, PermCheckCreateView):
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
        project_id = self.kwargs['pk']
        context['project'] = Project.objects.get(pk=project_id)
        context['other_projects'] = get_other_projects_html(project_id)
        return context

    def get_success_url(self):
        return self.request.GET.get('redirect', None) or reverse_lazy('issue_list', kwargs={'pk': self.kwargs.get('pk')})

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.add_issue', Project.objects.get(pk=self.kwargs['pk']))


class List(PermCheckListView):
    model = _model
    template_name = 'project/issues.html'
    context_object_name = 'issues'

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        project_id = self.kwargs['pk']
        context['project'] = Project.objects.get(pk=project_id)
        context['other_projects'] = get_other_projects_html(project_id)
        return context

    def get_queryset(self):
        return Issue.objects.filter(project__id=self.kwargs.get('pk')).order_by('-updated_on')

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.read_issue', Project.objects.get(pk=self.kwargs['pk']))


class Detail(PermCheckDetailView):
    model = _model
    template_name = 'project/issue_info.html'
    context_object_name = 'issue'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        context['other_projects'] = get_other_projects_html(self.object.project.id)

        context['comments'] = Comment.objects.filter(issue=self.object)
        context['comment_form'] = CommentForm(prefix=_comment_form_prefix)
        context['worktime_form'] = WorktimeForm(prefix=_worktime_form_prefix)
        context['spent_time'] = Worktime.objects.filter(issue=self.object)\
                                    .aggregate(Sum('hours')).get('hours__sum', 0) or 0
        context['form'] = _form(instance=self.object)
        context['subissues'] = Issue.objects.filter(parent=self.object)
        context['watch'] = True if self.request.user in self.object.watchers.all() else False
        return context

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.read_issue', Issue.objects.get(pk=self.kwargs['pk']).project)


class Update(PermCheckView):
    def __init__(self, **kwargs):
        self.object = None
        super(Update, self).__init__(**kwargs)
        return

    def get_object(self):
        assert self.kwargs.get('pk', False)
        self.object = Issue.objects.get(pk=self.kwargs['pk'])
        assert self.object
        return

    def get(self, request, *args, **kwargs):
        self.get_object()
        context = dict()
        context['issue'] = self.object
        context['project'] = self.object.project
        context['form'] = _form(instance=self.object)
        context['worktime_form'] = WorktimeBlankForm(prefix=_worktime_form_prefix)
        context['comment_form'] = CommentBlankForm(prefix=_comment_form_prefix)
        return render(request, 'project/edit_issue.html', context)

    def post(self, request, *args, **kwargs):
        self.get_object()
        error = False
        context = dict()

        if self.request.user.has_perm('pm.change_issue', self.object.project):
            post = self.request.POST.copy()
            post.update({'author': self.request.user.id})
            form = _form(post, instance=self.object)
            if form.is_valid():
                form.save()
            else:
                error = True
                context['form'] = form

        if self.request.user.has_perm('pm.add_worktime', self.object.project):
            worktime_form = WorktimeBlankForm(self.request.POST, prefix=_worktime_form_prefix)
            if worktime_form.is_valid() and not error:
                if worktime_form.cleaned_data['hours']:
                    worktime_form.cleaned_data['issue'] = self.object
                    worktime_form.cleaned_data['author'] = self.request.user
                    worktime_form.cleaned_data['date'] = time.strftime("%Y-%m-%d")
                    Worktime(**worktime_form.cleaned_data).save()
            else:
                error = True
                context['worktime_form'] = worktime_form

        if self.request.user.has_perm('pm.add_comment', self.object.project):
            comment_form = CommentBlankForm(self.request.POST, prefix=_comment_form_prefix)
            if comment_form.is_valid() and not error:
                if comment_form.cleaned_data['content']:
                    comment_form.cleaned_data['issue'] = self.object
                    comment_form.cleaned_data['author'] = self.request.user
                    Comment(**comment_form.cleaned_data).save()
            else:
                error = True
                context['comment_form'] = comment_form

        if error:
            context['issue'] = self.object
            context['project'] = self.object.project
            return render(request, 'project/edit_issue.html', context)
        else:
            from django.contrib import messages
            messages.success(self.request, update_success_message % self.object)

            return redirect('issue_detail', pk=kwargs['pk'])


class Delete(PermCheckView):
    def post(self, request, *args, **kwargs):
        issues = Issue.objects.filter(pk=kwargs['pk'])
        obj = issues[0]
        project_id = obj.project.id
        issues.delete()

        from django.contrib import messages
        messages.success(self.request, delete_success_message % obj)

        return HttpResponseRedirect(reverse('issue_list', kwargs={'pk': project_id}))

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.delete_issue', Issue.objects.get(pk=self.kwargs['pk']).project)


class CommentUpdate(PermCheckView):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        issue_id = Comment.objects.get(pk=pk).issue.id
        comment_form = CommentForm(request.POST, prefix=_comment_form_prefix)

        if comment_form.is_valid():
            Comment.objects.filter(pk=pk).update(**comment_form.cleaned_data)

        return HttpResponseRedirect(reverse('issue_detail', kwargs={'pk':issue_id}))

    def has_perm(self, request, *args, **kwargs):
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        return request.user.has_perm('pm.change_comment', comment.issue.project) or comment.author == request.user


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


class WorktimeList(PermCheckListView):
    model = Worktime
    template_name = 'project/worktimes.html'
    context_object_name = 'worktimes'

    def get_context_data(self, **kwargs):
        context = super(WorktimeList, self).get_context_data(**kwargs)
        issue = Issue.objects.get(pk=self.kwargs.get('pk'))
        context['issue'] = issue
        context['project'] = issue.project
        context['other_projects'] = get_other_projects_html(issue.project.id)
        return context

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.read_worktime', Issue.objects.get(pk=self.kwargs['pk']).project)


class WorktimeCreate(PermCheckCreateView):
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

    def has_perm(self, request, *args, **kwargs):
        return request.user.has_perm('pm.add_worktime', Issue.objects.get(pk=self.kwargs['pk']).project)


class WorktimeUpdate(PermCheckUpdateView):
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

    def get_form_kwargs(self):
        kwargs = super(WorktimeUpdate, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['author'] = self.request.user.id
            kwargs.update({
                'data': data,
            })
        return kwargs

    def has_perm(self, request, *args, **kwargs):
        worktime = Worktime.objects.get(pk=kwargs['pk'])
        project = worktime.issue.project
        user = self.request.user
        return user.has_perm('pm.change_worktime', project) or \
            (user.has_perm('pm.change_own_worktime', project) and user == worktime.author)


class WorktimeDelete(PermCheckView):
    def post(self, request, *args, **kwargs):
        query_set = Worktime.objects.filter(pk=kwargs['pk'])
        issue_id = query_set[0].issue.id
        query_set.delete()
        return HttpResponseRedirect(reverse('worktime_list', kwargs={'pk': issue_id}))

    def has_perm(self, request, *args, **kwargs):
        worktime = Worktime.objects.get(pk=kwargs['pk'])
        project = worktime.issue.project
        user = self.request.user
        return user.has_perm('pm.change_worktime', project) or \
            (user.has_perm('pm.change_own_worktime', project) and user == worktime.author)


class AllIssues(ListView):
    model = _model
    template_name = 'all_issues.html'
    context_object_name = 'issues'

    def get_context_data(self, **kwargs):
        context = super(AllIssues, self).get_context_data(**kwargs)
        version_id = self.request.GET.get('version_id', None)
        open = True if 'open' in self.request.GET else False
        status_id = self.request.GET.get('status_id', None)
        issue_tag_id = self.request.GET.get('issue_tag_id', None)
        assigned_to_id = self.request.GET.get('assigned_to_id', None)
        watcher_id = self.request.GET.get('watcher_id', None)

        issues = Issue.objects.all()
        if version_id:
            issues = issues.filter(version_id=version_id)

        if open:
            issues = issues.exclude(status_id=Version.CLOSED_STATUS)
        else:
            if status_id:
                issues = issues.filter(status_id=status_id)

        if issue_tag_id:
            issues = issues.filter(tag_id=issue_tag_id)

        if assigned_to_id:
            issues = issues.filter(assigned_to_id=assigned_to_id)

        if watcher_id:
            issues = issues.filter(watchers__id=watcher_id)

        context['issues'] = issues
        return context


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
        # context['watch_issues'] = [n.issue for n in Issue.watchers.through.objects.filter(user=self.request.user)]
        context['watch_issues'] = Issue.objects.filter(watchers=self.request.user)
        return render(request, 'my_page.html', context)

