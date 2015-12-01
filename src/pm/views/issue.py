# coding:utf-8
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Sum
from ..forms import IssueForm, CommentForm, WorktimeForm
from ..models import Issue, Comment, Worktime, Project
from ..utils import Helper
import time


_model = Issue
_form = IssueForm
_worktime_prefix = 'worktime'
_comment_prefix = 'comment'


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
            data['author'] = u'1'                               # TODO: use login user
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


class Detail(DetailView):
    model = _model
    template_name = 'project/issue_info.html'
    context_object_name = 'issue'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        context['comments'] = Comment.objects.filter(issue=self.object)
        context['comment_form'] = CommentForm(prefix=_comment_prefix)
        context['worktime_form'] = WorktimeForm(prefix=_worktime_prefix)
        context['spent_time'] = Worktime.objects.filter(issue=self.object)\
                                    .aggregate(Sum('hours')).get('hours__sum', 0) or 0
        context['form'] = _form(instance=self.object)
        context['subissues'] = Issue.objects.filter(parent=self.object)
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
        context['worktime_form'] = WorktimeForm(prefix=_worktime_prefix)
        context['comment_form'] = CommentForm(prefix=_comment_prefix)
        return context

    def get_form_kwargs(self):
        kwargs = super(Update, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()
            data['author'] = u'1'                               # TODO: use login user
            kwargs.update({
                'data': data,
            })
        return kwargs

    def form_valid(self, form):
        worktime_form = WorktimeForm(self.request.POST, prefix=_worktime_prefix)
        comment_form = CommentForm(self.request.POST, prefix='comment')
        if worktime_form.is_valid():
            worktime_form.cleaned_data['project'] = self.object.project
            worktime_form.cleaned_data['issue'] = self.object
            worktime_form.cleaned_data['author_id'] = u'1'              # TODO: use login user
            worktime_form.cleaned_data['date'] = time.strftime("%Y-%m-%d")
            Worktime(**worktime_form.cleaned_data).save()
        else:
            if 'hours' in worktime_form.cleaned_data:
                return super(Update, self).form_invalid(form)

        if comment_form.is_valid():
            comment_form.cleaned_data['issue'] = self.object
            comment_form.cleaned_data['author_id'] = u'1'               # TODO: use login user
            Comment(**comment_form.cleaned_data).save()
        else:
            return super(Update, self).form_invalid(form)

        return super(Update, self).form_valid(form)


    '''
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
    '''


class Delete(View):
    def post(self, request, *args, **kwargs):
        issues = Issue.objects.filter(pk=kwargs['pk'])
        project_id = issues[0].project.id
        issues.delete()
        return HttpResponseRedirect(reverse('issue_list', kwargs={'pk': project_id}))


class CommentUpdate(View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        comment_form = CommentForm(request.POST, prefix=_comment_prefix)

        if comment_form.is_valid():
            Comment.objects.filter(pk=pk).update(**comment_form.cleaned_data)

        return HttpResponseRedirect(reverse('issue_detail', kwargs={'pk':pk}))


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
