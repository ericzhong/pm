from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test


class homepage(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


def admin_required(function=None, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser,
        login_url='/',               # can not use reverse() in urlconf
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
