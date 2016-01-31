from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from .setting import anonymous_access


class homepage(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


def admin_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser,
        login_url='/',               # can not use reverse() in urlconf
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def anonymous_perm(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: True if anonymous_access() else u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
