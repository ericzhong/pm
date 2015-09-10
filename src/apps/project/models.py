# coding:utf-8
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User


@python_2_unicode_compatible
class Projects(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    homepage = models.CharField(max_length=255, default='', blank=True)
    is_public = models.BooleanField(default=True)
    parent_id = models.ForeignKey('Projects')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(null=True)
    identifier = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.IntegerField(default=1)     # built-in: open,closed
    inherit_members = models.BooleanField(default=False)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Issues(models.Model):
    issue_type = models.ForeignKey('IssueTypes')
    project_id = models.ForeignKey('Projects')
    subject = models.CharField(max_length=255, default='')
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.ForeignKey('IssueStatuses')
    assigned_to = models.ForeignKey(User, null=True)
    priority = models.IntegerField(default=1)       # built-in (low,normal,high,emergency,immediately)
    version = models.ForeignKey('Versions')
    author =  models.ForeignKey(User, related_name='created_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(null=True)
    done_ratio = models.IntegerField(default=0)
    parent_id = models.ForeignKey('Issues')
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.subject


@python_2_unicode_compatible
class IssueTypes(models.Model):
    name = models.CharField(max_length=30, default='')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class IssueStatuses(models.Model):
    name = models.CharField(max_length=30, default='')
    default_done_ratio = models.IntegerField()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Versions(models.Model):
    project = models.ForeignKey('Projects')
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(null=True)
    wiki_page = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(default=1)     # built-in (open,locked,closed)
    effective_date = models.DateTimeField()

    def __str__(self):
        return self.name

