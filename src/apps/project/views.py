from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from .models import Project
from .forms import ProjectForm


class ProjectList(ListView):
    model = Project
    template_name = 'project/project_list.html'
    context_object_name = 'projects'


class ProjectDetail(DetailView):
    model = Project
    template_name = 'project/project_detail.html'
    context_object_name = 'project'


class ProjectCreate(CreateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project_list')


class ProjectUpdate(UpdateView):
    model = Project
    form_class = ProjectForm

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})


class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('project_list')