# coding:utf-8
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User


@python_2_unicode_compatible
class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    homepage = models.CharField(max_length=255, default='', blank=True)
    is_public = models.BooleanField(default=True)
    parent = models.ForeignKey('Project', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    identifier = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.IntegerField(default=1)     # built-in: open,closed
    inherit_members = models.BooleanField(default=False)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Issue(models.Model):
    issue_type = models.ForeignKey('IssueType')
    project = models.ForeignKey('Project')
    subject = models.CharField(max_length=255, default='')
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey('IssueStatus')
    assigned_to = models.ForeignKey(User, null=True, blank=True)
    priority = models.IntegerField(default=1)       # built-in (low,normal,high,emergency,immediately)
    version = models.ForeignKey('Version', null=True, blank=True)
    author = models.ForeignKey(User, related_name='created_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    done_ratio = models.IntegerField(default=0)
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
    project = models.ForeignKey('Project')
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    wiki_page = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(default=1)     # built-in (open,locked,closed)
    effective_date = models.DateField()

    class Meta:
        unique_together = ("project", "name")

    def __str__(self):
        return self.name

