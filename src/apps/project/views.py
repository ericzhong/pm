from django.views.generic import ListView, DetailView
from .models import Project


class ProjectList(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'


class ProjectDetail(DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'
