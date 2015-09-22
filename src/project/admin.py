from django.contrib import admin
from .models import *
from .forms import *



class ProjectModelAdmin(admin.ModelAdmin):
    form = ProjectForm
    list_display = ('id', 'name')
    ordering = ('-id',)


class IssueAdmin(admin.ModelAdmin):
    form = IssueForm
    list_display = ('id', 'subject')
    ordering = ('-id',)


class IssueTypeAdmin(admin.ModelAdmin):
    form = IssueTypeForm
    list_display = ('id', 'name')
    ordering = ('id',)


class IssueStatusAdmin(admin.ModelAdmin):
    form = IssueStatusForm
    list_display = ('id', 'name')
    ordering = ('id',)


class VersionAdmin(admin.ModelAdmin):
    form = VersionForm
    list_display = ('project', 'name')
    ordering = ('project', 'name')


class MemberAdmin(admin.ModelAdmin):
    form = MemberForm
    list_display = ('project', 'user')
    ordering = ('project',)



admin.site.register(Project, ProjectModelAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(IssueType, IssueTypeAdmin)
admin.site.register(IssueStatus, IssueStatusAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Member, MemberAdmin)
