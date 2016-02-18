# coding:utf-8
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import ugettext as _


_STRING_MAX_LENGTH = 255


def _get_estimated_time(issues):
    n = 0
    for issue in issues:
        if issue.start_date and issue.due_date and issue.start_date <= issue.due_date:
            n += (issue.due_date - issue.start_date).days + 1
    return n * 8


class User(AbstractUser):

    @property
    def get_full_name(self):
        # TODO: formatted by settings
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()


@python_2_unicode_compatible
class Project(models.Model):

    class Meta:
        default_permissions = ()
        # put all permissions here.
        permissions = (
            ("add_project", "Add project"),
            ("change_project", "Change project"),
            ("close_project", "Close project"),
            ("add_subproject", "Add subproject"),
            ("manage_member", "Manage member"),
            ("manage_version", "Manage version"),
            ("manage_issue_category", "Manage issue category"),
            ("read_gantt", "Read Gantt"),
            ("add_issue", "Add issue"),
            ("change_issue", "Change issue"),
            ("read_issue", "Read issue"),
            ("delete_issue", "Delete issue"),
            ("add_comment", "Add comment"),
            ("change_comment", "Change comment"),
            ("add_worktime", "Add worktime"),
            ("read_worktime", "Read worktime"),
            ("change_worktime", "Change worktime"),
            ("change_own_worktime", "Change own worktime"),
        )

    OPEN_STATUS = 1
    CLOSED_STATUS = 2

    STATUS_CHOICES = (
        (OPEN_STATUS, _('open')),
        (CLOSED_STATUS, _('closed')),
    )

    name = models.CharField(max_length=_STRING_MAX_LENGTH, unique=True)
    description = models.TextField(null=True, blank=True)
    homepage = models.CharField(max_length=_STRING_MAX_LENGTH, default='', blank=True)
    is_public = models.BooleanField(default=True)
    parent = models.ForeignKey('Project', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    identifier = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.IntegerField(default=OPEN_STATUS, choices=STATUS_CHOICES)
    inherit_members = models.BooleanField(default=False)
    created_by = models.ForeignKey('User', related_name='creator')

    def __str__(self):
        return self.name

    def issue_report(self):
        issues = Issue.objects.filter(project=self)

        import collections
        data = collections.defaultdict(dict)
        for issue in issues:
            if Version.STATUS_CHOICES[Version.CLOSED_STATUS-1][1] == issue.status.name:
                data[issue.tag]['closed'] = data[issue.tag].get('closed', 0) + 1
            else:
                data[issue.tag]['open'] = data[issue.tag].get('open', 0) + 1

        for key, value in data.iteritems():
            data[key]['total'] = data[key].get('open', 0) + data[key].get('closed', 0)

        return dict(data)

    def estimated_time(self):
        return _get_estimated_time(Issue.objects.filter(project=self))

    def spent_time(self):
        return Issue.objects.filter(project=self).aggregate(hours=models.Sum('worktime__hours'))['hours'] or 0

    issue_report = property(issue_report)
    estimated_time = property(estimated_time)
    spent_time = property(spent_time)


@python_2_unicode_compatible
class Issue(models.Model):

    class Meta:
        default_permissions = ()

    LOW_PRIORITY = 1
    NORMAL_PRIORITY = 2
    HIGH_PRIORITY = 3
    EMERGENCY_PRIORITY = 4
    IMMEDIATELY_PRIORITY = 5

    PRIORITY_CHOICES = (
        (LOW_PRIORITY, _('Low')),
        (NORMAL_PRIORITY, _('Normal')),
        (HIGH_PRIORITY, _('High')),
        (EMERGENCY_PRIORITY, _('Emergency')),
        (IMMEDIATELY_PRIORITY, _('Immediately')),
    )

    DONE_RATIO_CHOICES = tuple((n, str(n)+"%") for n in range(0, 101, 10))

    tag = models.ForeignKey('IssueTag')
    category = models.ForeignKey('IssueCategory', null=True, blank=True)
    project = models.ForeignKey('Project')
    subject = models.CharField(max_length=_STRING_MAX_LENGTH)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey('IssueStatus')
    assigned_to = models.ForeignKey('User', null=True, blank=True)
    priority = models.IntegerField(default=NORMAL_PRIORITY, choices=PRIORITY_CHOICES)
    version = models.ForeignKey('Version', null=True, blank=True)
    author = models.ForeignKey('User', related_name='created_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    done_ratio = models.IntegerField(default=0, choices=DONE_RATIO_CHOICES)
    parent = models.ForeignKey('Issue', null=True, blank=True)
    is_private = models.BooleanField(default=False)
    watchers = models.ManyToManyField('User', related_name='watchers')

    def __str__(self):
        return self.subject


@python_2_unicode_compatible
class IssueCategory(models.Model):
    name = models.CharField(max_length=_STRING_MAX_LENGTH)
    project = models.ForeignKey('Project')

    class Meta:
        default_permissions = ()
        unique_together = ("project", "name")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class IssueTag(models.Model):
    name = models.CharField(max_length=_STRING_MAX_LENGTH, unique=True)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class IssueStatus(models.Model):
    name = models.CharField(max_length=_STRING_MAX_LENGTH, unique=True)
    #default_done_ratio = models.IntegerField(null=True, blank=True)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Version(models.Model):

    OPEN_STATUS = 1
    LOCKED_STATUS = 2
    CLOSED_STATUS = 3

    STATUS_CHOICES = (
        (OPEN_STATUS, _('open')),
        (LOCKED_STATUS, _('locked')),
        (CLOSED_STATUS, _('closed')),
    )

    project = models.ForeignKey('Project')
    name = models.CharField(max_length=_STRING_MAX_LENGTH)
    description = models.CharField(max_length=_STRING_MAX_LENGTH, default="", blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    wiki_page = models.CharField(max_length=_STRING_MAX_LENGTH, default="", blank=True)
    status = models.IntegerField(default=OPEN_STATUS, choices=STATUS_CHOICES)
    effective_date = models.DateField(null=True, blank=True)

    class Meta:
        default_permissions = ()
        unique_together = ("project", "name")

    def total_issue(self):
        return Issue.objects.filter(version=self).count()

    def total_open_issue(self):
        return Issue.objects.filter(version=self).exclude(status__id=self.CLOSED_STATUS).count()

    def total_closed_issue(self):
        return Issue.objects.filter(version=self).filter(status__id=self.CLOSED_STATUS).count()

    def issues(self):
        return Issue.objects.filter(version=self)

    def done_ratio(self):
        return int(Issue.objects.filter(version=self)
                   .exclude(status__id=self.CLOSED_STATUS)
                   .aggregate(data=models.Avg('done_ratio'))['data'])

    def estimated_time(self):
        return _get_estimated_time(Issue.objects.filter(version=self))

    def spent_time(self):
        return Issue.objects.filter(version=self).aggregate(hours=models.Sum('worktime__hours'))['hours'] or 0

    total_issue = property(total_issue)
    total_open_issue = property(total_open_issue)
    total_closed_issue = property(total_closed_issue)
    issues = property(issues)
    done_ratio = property(done_ratio)
    estimated_time = property(estimated_time)
    spent_time = property(spent_time)

    def __str__(self):
        return self.name


class Project_User_Role(models.Model):
    project = models.ForeignKey('Project')
    user = models.ForeignKey('User')
    role = models.ForeignKey('Role')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
        unique_together = ('project', 'user', 'role')


class Project_Group_Role(models.Model):
    project = models.ForeignKey('Project')
    group = models.ForeignKey(Group)
    role = models.ForeignKey('Role')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
        unique_together = ('project', 'group', 'role')


class Comment(models.Model):
    issue = models.ForeignKey('Issue')
    author = models.ForeignKey('User', related_name='author')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()

    class Meta:
        default_permissions = ()


class Worktime(models.Model):
    issue = models.ForeignKey('Issue')
    author = models.ForeignKey('User')
    hours = models.IntegerField()
    date = models.DateField()
    description = models.CharField(max_length=_STRING_MAX_LENGTH, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ()


@python_2_unicode_compatible
class Role(models.Model):
    name = models.CharField(max_length=_STRING_MAX_LENGTH, unique=True)
    permissions = models.ManyToManyField(Permission)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.name


class Setting(models.Model):
    name = models.CharField(max_length=_STRING_MAX_LENGTH, unique=True)
    value = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ()


@python_2_unicode_compatible
class Profile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True)
    avatar = models.CharField(max_length=_STRING_MAX_LENGTH)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return "%s's profile" % self.user
