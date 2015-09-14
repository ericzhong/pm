from django.contrib import admin
from .models import Project, Issue, IssueStatus, IssueType, Version
from .forms import ProjectForm



class ProjectModelAdmin(admin.ModelAdmin):
    form = ProjectForm

admin.site.register(Project, ProjectModelAdmin)
admin.site.register(Issue)

class IssueTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id',)

admin.site.register(IssueType, IssueTypeAdmin)


class IssueStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id',)

admin.site.register(IssueStatus, IssueStatusAdmin)


class VersionAdmin(admin.ModelAdmin):
    list_display = ('project', 'name')
    ordering = ('project',)

admin.site.register(Version, VersionAdmin)
