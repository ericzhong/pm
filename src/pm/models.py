# coding:utf-8
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


@python_2_unicode_compatible
class Project(models.Model):

    OPEN_STATUS = 1
    CLOSED_STATUS = 2

    STATUS_CHOICES = (
        (OPEN_STATUS, _('open')),
        (CLOSED_STATUS, _('closed')),
    )

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    homepage = models.CharField(max_length=255, default='', blank=True)
    is_public = models.BooleanField(default=True)
    parent = models.ForeignKey('Project', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    identifier = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    inherit_members = models.BooleanField(default=False)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Issue(models.Model):

    PRIORITY_CHOICES = (
        (1, _('Low')),
        (2, _('Normal')),
        (3, _('High')),
        (4, _('Emergency')),
        (5, _('Immediately')),
    )

    DONE_RATIO_CHOICES = tuple((n, str(n)+" %") for n in range(0, 101, 10))

    issue_type = models.ForeignKey('IssueType')
    project = models.ForeignKey('Project')
    subject = models.CharField(max_length=255, default='')
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey('IssueStatus')
    assigned_to = models.ForeignKey(User, null=True, blank=True)
    priority = models.IntegerField(default=1, choices=PRIORITY_CHOICES)
    version = models.ForeignKey('Version', null=True, blank=True)
    author = models.ForeignKey(User, related_name='created_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    done_ratio = models.IntegerField(default=0, choices=DONE_RATIO_CHOICES)
    parent = models.ForeignKey('Issue', null=True, blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.subject


@python_2_unicode_compatible
class IssueType(models.Model):
    name = models.CharField(max_length=30, default='', unique=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class IssueStatus(models.Model):
    name = models.CharField(max_length=30, default='', unique=True)
    default_done_ratio = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Version(models.Model):

    STATUS_CHOICES = (
        (1, _('open')),
        (2, _('locked')),
        (3, _('closed')),
    )

    project = models.ForeignKey('Project')
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    wiki_page = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    effective_date = models.DateField()

    class Meta:
        unique_together = ("project", "name")

    def __str__(self):
        return self.name


class Member(models.Model):
    project = models.ForeignKey('Project')
    user = models.ForeignKey(User, related_name='member')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "user")


class Comment(models.Model):
    issue = models.ForeignKey('Issue')
    author = models.ForeignKey(User, related_name='author')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()


class Worktime(models.Model):
    project = models.ForeignKey('Project')
    issue = models.ForeignKey('Issue')
    author = models.ForeignKey(User)
    hours = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    comment = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)