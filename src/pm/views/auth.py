from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from ..forms import UserForm

_model = User
_form = UserForm

class MyAccount(UpdateView):
    model = _model
    form_class = _form
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self, queryset=None):
        return self.request.user