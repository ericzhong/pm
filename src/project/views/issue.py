# coding:utf-8
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from ..forms import IssueForm, CommentForm
from ..models import Issue, Comment
from ..utils import Helper


_model = Issue
_form = IssueForm
_template_dir = 'issue'
_name = 'issue'
_plural = 'issues'


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
        if object.start_date is not None:
            object.start_date = object.start_date.strftime('%Y-%m-%d')
        if object.due_date is not None:
            object.due_date = object.due_date.strftime('%Y-%m-%d')
        return object

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data()
        context['comments'] = Comment.objects.filter(issue=context['object'])
        context['comment_form'] = CommentForm()
        return context


class Create(CreateView):
    model = _model
    template_name = '%s/form.html' % _template_dir
    form_class = _form
    success_url = reverse_lazy('%s_list' % _name)


class Update(View):
    template_name = '%s/form.html' % _template_dir

    def get(self, request, **kwargs):
        issue = Issue.objects.get(pk=kwargs['pk'])
        issue_form = IssueForm(prefix='issue', instance=issue)

        # Quote
        comment_id = request.GET.get('quote', None)
        comment = None
        if comment_id is not None:
            comment = Comment.objects.get(id=comment_id)
            comment.content = "%s:\n%s" % (comment.author.username, Helper.quote(comment.content))
        comment_form = CommentForm(instance=comment, prefix='comment')
        return render(request, self.template_name, {'form': {'issue': issue_form, 'comment': comment_form}})

    def post(self, request, **kwargs):
        pk = kwargs['pk']
        issue_form = IssueForm(request.POST, prefix='issue')
        comment_form = CommentForm(request.POST, prefix='comment')

        if issue_form.is_valid():
            Issue.objects.filter(pk=pk).update(**issue_form.cleaned_data)
            if comment_form.is_valid():
                comment_form.cleaned_data['issue_id'] = pk
                comment_form.cleaned_data['author_id'] = request.user.id
                Comment(**comment_form.cleaned_data).save()
            return HttpResponseRedirect(reverse('%s_detail' % _name, kwargs={'pk': pk}))
        else:
            return render(request, self.template_name, {'form': {'issue': issue_form, 'comment': comment_form}})


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