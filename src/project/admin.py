from django.contrib import admin
from .models import Project, Issue, IssueStatus, IssueType, Version
from .forms import ProjectForm, IssueForm, IssueTypeForm, IssueStatusForm, VersionForm



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


admin.site.register(Project, ProjectModelAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(IssueType, IssueTypeAdmin)
admin.site.register(IssueStatus, IssueStatusAdmin)
admin.site.register(Version, VersionAdmin)
