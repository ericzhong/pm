from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from ..forms import UserAccountForm


class MyAccount(UpdateView):
    model = User
    form_class = UserAccountForm
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self, queryset=None):
        return self.request.user
