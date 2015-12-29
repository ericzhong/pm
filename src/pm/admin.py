from django.contrib import admin
from .forms import *



class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
    list_display = ('id', 'name')
    ordering = ('-id',)


class IssueAdmin(admin.ModelAdmin):
    form = IssueForm
    list_display = ('id', 'subject')
    ordering = ('-id',)


class IssueTagAdmin(admin.ModelAdmin):
    form = IssueTagForm
    list_display = ('id', 'name')
    ordering = ('id',)


class IssueCategoryAdmin(admin.ModelAdmin):
    form = IssueCategoryForm
    list_display = ('id', 'project', 'name')
    ordering = ('project',)


class IssueStatusAdmin(admin.ModelAdmin):
    form = IssueStatusForm
    list_display = ('id', 'name')
    ordering = ('id',)


class VersionAdmin(admin.ModelAdmin):
    form = VersionForm
    list_display = ('project', 'name')
    ordering = ('project', 'name')


admin.site.register(Project, ProjectAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(IssueTag, IssueTagAdmin)
admin.site.register(IssueCategory, IssueCategoryAdmin)
admin.site.register(IssueStatus, IssueStatusAdmin)
admin.site.register(Version, VersionAdmin)
