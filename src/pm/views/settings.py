from django.views.generic import UpdateView
from django.core.urlresolvers import reverse_lazy
from ..models import Settings
from ..forms import UpdateSettingsForm
from .auth import SuperuserRequiredMixin
from .base import UpdateSuccessMessageMixin

_model = Settings
_form = UpdateSettingsForm


class Update(SuperuserRequiredMixin, UpdateSuccessMessageMixin, UpdateView):
    model = _model
    form_class = _form
    template_name = '_admin/settings.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=1)

    def get_success_url(self):
        return reverse_lazy('settings')


def allow_anonymous_access():
    return True     # TODO: data from settings


def page_size():
    return 3        # TODO
