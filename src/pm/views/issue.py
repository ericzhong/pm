# coding:utf-8
from django.views.generic import ListView, View, CreateView, UpdateView, DetailView
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Sum
from django.shortcuts import render, redirect
from ..forms import IssueForm, CommentForm, WorktimeForm, WorktimeBlankForm, CommentBlankForm, AllIssuesForm, \
    UpdateIssueForm
from ..models import Issue, Comment, Worktime, Project, IssueStatus
from ..utils import Helper
from .project import get_other_projects_html, get_visible_projects
from .auth import PermissionMixin, redirect_no_perm, LoginRequiredMixin
from .base import CreateSuccessMessageMixin, UpdateSuccessMessageMixin, \
    update_success_message, delete_success_message
import time

_model = Issue
_form = IssueForm
_worktime_form_prefix = 'worktime'
_comment_form_prefix = 'comment'


class Create(PermissionMixin, CreateSuccessMessageMixin, CreateView):
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
        return self.request.GET.get('redirect', None) or reverse_lazy('issue_list',
                                                                      kwargs={'pk': self.kwargs.get('pk')})

    def has_perm(self):
        user = self.request.user
        return user.is_authenticated() and user.has_perm('pm.add_issue', Project.objects.get(pk=self.kwargs['pk']))


class List(PermissionMixin, ListView):
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

    def has_perm(self):
        return self.request.user.has_perm('pm.read_issue', Project.objects.get(pk=self.kwargs['pk']))


class Detail(PermissionMixin, DetailView):
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
        context['spent_time'] = Worktime.objects.filter(issue=self.object) \
                                    .aggregate(Sum('hours')).get('hours__sum', 0) or 0
        context['form'] = _form(instance=self.object)
        context['subissues'] = Issue.objects.filter(parent=self.object)
        context['watch'] = True if self.request.user in self.object.watchers.all() else False
        return context

    def has_perm(self):
        return self.request.user.has_perm('pm.read_issue', Issue.objects.get(pk=self.kwargs['pk']).project)


class Update(PermissionMixin, View):
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

        user = self.request.user
        if not user.has_perm('pm.change_issue', self.object.project) and \
                not user.has_perm('pm.add_worktime', self.object.project) and \
                not user.has_perm('pm.add_comment', self.object.project):
            return redirect_no_perm()

        context = dict()
        context['issue'] = self.object
        context['project'] = self.object.project
        context['form'] = UpdateIssueForm(instance=self.object)
        context['worktime_form'] = WorktimeBlankForm(prefix=_worktime_form_prefix)
        context['comment_form'] = CommentBlankForm(prefix=_comment_form_prefix)
        return render(request, 'project/edit_issue.html', context)

    def post(self, request, *args, **kwargs):
        self.get_object()

        user = self.request.user
        if not user.has_perm('pm.change_issue', self.object.project) and \
                not user.has_perm('pm.add_worktime', self.object.project) and \
                not user.has_perm('pm.add_comment', self.object.project):
            return redirect_no_perm()

        error = False
        context = dict()

        if user.has_perm('pm.change_issue', self.object.project):
            form = UpdateIssueForm(self.request.POST, instance=self.object)      # instance to update
            if form.is_valid():
                form.save()
            else:
                error = True
                context['form'] = form

        if user.has_perm('pm.add_worktime', self.object.project):
            worktime_form = WorktimeBlankForm(self.request.POST, prefix=_worktime_form_prefix)
            if worktime_form.is_valid() and not error:
                if worktime_form.cleaned_data['hours']:
                    worktime_form.cleaned_data['issue'] = self.object
                    worktime_form.cleaned_data['author'] = user
                    worktime_form.cleaned_data['date'] = time.strftime("%Y-%m-%d")
                    Worktime(**worktime_form.cleaned_data).save()
            else:
                error = True
                context['worktime_form'] = worktime_form

        if user.has_perm('pm.add_comment', self.object.project):
            comment_form = CommentBlankForm(self.request.POST, prefix=_comment_form_prefix)
            if comment_form.is_valid() and not error:
                if comment_form.cleaned_data['content']:
                    comment_form.cleaned_data['issue'] = self.object
                    comment_form.cleaned_data['author'] = user
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


class Delete(PermissionMixin, View):
    def post(self, request, *args, **kwargs):
        issues = Issue.objects.filter(pk=kwargs['pk'])
        project_id = issues[0].project.id

        from django.contrib import messages
        messages.success(self.request, delete_success_message % issues[0])

        issues.delete()
        return HttpResponseRedirect(reverse('issue_list', kwargs={'pk': project_id}))

    def has_perm(self):
        issue = Issue.objects.get(pk=self.kwargs['pk'])
        user = self.request.user
        return user.has_perm('pm.delete_issue', issue.project) or \
            (user.has_perm('pm.delete_own_issue', issue.project) and issue.author == user)


class CommentUpdate(PermissionMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        issue_id = Comment.objects.get(pk=pk).issue.id
        comment_form = CommentForm(request.POST, prefix=_comment_form_prefix)

        if comment_form.is_valid():
            Comment.objects.filter(pk=pk).update(**comment_form.cleaned_data)

        return HttpResponseRedirect(reverse('issue_detail', kwargs={'pk': issue_id}))

    def has_perm(self):
        user = self.request.user
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        if user.has_perm('pm.change_comment', comment.issue.project):
            return True
        return user.is_authenticated() and \
            user.has_perm('pm.change_own_comment', comment.issue.project) and \
            comment.author == user


class Quote(PermissionMixin, View):
    def get(self, request, *args, **kwargs):
        data = dict()
        comment_id = request.GET.get('comment', None)  # URL?comment=id
        if comment_id is not None:
            comment = Comment.objects.get(pk=comment_id)
            data['content'] = "%s wrote:\n%s" % (comment.author.username, Helper.quote(comment.content))
        else:
            data['content'] = ""
        return JsonResponse(data)

    def has_perm(self):
        user = self.request.user
        return user.is_authenticated() and \
            user.has_perm('pm.add_comment', Issue.objects.get(pk=self.request['pk']).project)


class WorktimeList(PermissionMixin, ListView):
    model = Worktime
    template_name = 'project/worktimes.html'
    context_object_name = 'worktimes'

    def get_context_data(self, **kwargs):
        context = super(WorktimeList, self).get_context_data(**kwargs)
        issue = Issue.objects.get(pk=self.kwargs['pk'])
        context['issue'] = issue
        context['project'] = issue.project
        context['other_projects'] = get_other_projects_html(issue.project.id)
        return context

    def get_queryset(self):
        return Worktime.objects.filter(issue__id=self.kwargs['pk']).order_by('-date')

    def has_perm(self):
        return self.request.user.has_perm('pm.read_worktime', Issue.objects.get(pk=self.kwargs['pk']).project)


class WorktimeCreate(PermissionMixin, CreateSuccessMessageMixin, CreateView):
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

    def has_perm(self):
        user = self.request.user
        return user.is_authenticated() and \
            user.has_perm('pm.add_worktime', Issue.objects.get(pk=self.kwargs['pk']).project)


class WorktimeUpdate(PermissionMixin, UpdateSuccessMessageMixin, UpdateView):
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

    def has_perm(self):
        worktime = Worktime.objects.get(pk=self.kwargs['pk'])
        project = worktime.issue.project
        user = self.request.user
        if user.has_perm('pm.change_worktime', project):
            return True
        return user.is_authenticated() and \
            user.has_perm('pm.change_own_worktime', project) and user == worktime.author


class WorktimeDelete(PermissionMixin, View):
    def post(self, request, *args, **kwargs):
        query_set = Worktime.objects.filter(pk=kwargs['pk'])
        issue_id = query_set[0].issue.id

        from django.contrib import messages
        messages.success(self.request, delete_success_message % query_set[0])

        query_set.delete()
        return HttpResponseRedirect(reverse('worktime_list', kwargs={'pk': issue_id}))

    def has_perm(self):
        worktime = Worktime.objects.get(pk=self.kwargs['pk'])
        project = worktime.issue.project
        user = self.request.user
        if user.has_perm('pm.delete_worktime', project):
            return True
        return user.is_authenticated() and \
            user.has_perm('pm.delete_own_worktime', project) and user == worktime.author


class AllIssues(PermissionMixin, ListView):
    model = _model
    template_name = 'all_issues.html'
    context_object_name = 'issues'

    def __init__(self, *args, **kwargs):
        super(AllIssues, self).__init__(*args, **kwargs)
        self.order = ''
        from .settings import page_size
        self.page_size = page_size()

    def get_context_data(self, **kwargs):
        context = super(AllIssues, self).get_context_data(**kwargs)
        context['form'] = AllIssuesForm(
            initial={n: self.request.GET.get(n, None) for n in AllIssuesForm.declared_fields},
            user=self.request.user)
        context['order'] = self.order
        context['paging'] = {'length': self.length,
                             'offset': self.offset,
                             'page_size': self.page_size}
        return context

    def get_queryset(self):
        project = self.request.GET.get('project', None)
        version = self.request.GET.get('version', None)
        tag = self.request.GET.get('tag', None)
        status = self.request.GET.get('status', None)
        priority = self.request.GET.get('priority', None)
        assignee = self.request.GET.get('assignee', None)
        watcher = self.request.GET.get('watcher', None)
        start_date = self.request.GET.get('start_date', None)
        due_date = self.request.GET.get('due_date', None)
        offset = self.request.GET.get('offset', None)
        order = self.request.GET.get('order', None)

        projects = get_visible_projects(self.request.user)
        issues = Issue.objects.filter(project__in=projects)

        if project:
            issues = issues.filter(project__id=project)

        if version:
            issues = issues.filter(version__id=version)

        if tag:
            issues = issues.filter(tag_id=tag)

        if status:
            if int(status) == IssueStatus.NOT_CLOSED_STATUS:
                issues = issues.exclude(status__id=IssueStatus.CLOSED_STATUS)
            else:
                issues = issues.filter(status__id=status)

        if assignee:
            issues = issues.filter(assigned_to_id=assignee)

        if watcher:
            issues = issues.filter(watchers__id=watcher)

        if priority:
            issues = issues.filter(priority=priority)

        if start_date:
            issues = issues.filter(start_date__gte=start_date)

        if due_date:
            issues = issues.filter(due_date__lte=due_date)

        if order in ['id', 'project', 'version', 'tag',
                     'status', 'priority', 'subject', 'assigned_to', 'updated_on',
                     '-id', '-project', '-version', '-tag',
                     '-status', '-priority', '-subject', '-assigned_to', '-updated_on']:
            issues = issues.order_by(order)
            self.order = order

        self.length = len(issues)

        try:
            offset = int(offset) if offset else 0
        except ValueError:
            offset = 0
        issues = issues[offset:offset+self.page_size]
        self.offset = offset

        return issues

    def has_perm(self):
        return self.request.user.has_perm("pm.read_issue")


class Watch(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        Issue.watchers.through.objects.get_or_create(user=self.request.user, issue_id=pk)
        return redirect('issue_detail', pk=pk)


class Unwatch(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        Issue.watchers.through.objects.filter(user=self.request.user, issue_id=pk).delete()
        return redirect('issue_detail', pk=pk)


class MyPage(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context['assigned_issues'] = Issue.objects.filter(assigned_to=self.request.user)
        context['watch_issues'] = Issue.objects.filter(watchers=self.request.user)
        return render(request, 'my_page.html', context)
