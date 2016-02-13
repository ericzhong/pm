from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from .setting import anonymous_access
from .role import get_group_permissions, get_project_group_permissions, \
    get_user_permissions, get_project_user_permissions


class AuthBackend(ModelBackend):
    def _get_user_permissions(self, user_obj, obj=None):
        if obj is None:
            return get_user_permissions(user_obj)
        else:
            return get_project_user_permissions(user_obj, obj)

    def _get_group_permissions(self, user_obj, obj=None):
        if obj is None:
            return get_group_permissions(user_obj)
        else:
            return get_project_group_permissions(user_obj, obj)

    def _get_permissions(self, user_obj, obj, from_name):
        """
        Returns the permissions of `user_obj` from `from_name`. `from_name` can
        be either "group" or "user" to return permissions from
        `_get_group_permissions` or `_get_user_permissions` respectively.
        """
        if not user_obj.is_active or user_obj.is_anonymous():
            return set()

        perm_cache_name = '_%s_perm_cache' % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, '_get_%s_permissions' % from_name)(user_obj, obj)
            perms = [(p.content_type.app_label, p.codename) for p in perms]
            setattr(user_obj, perm_cache_name, set("%s.%s" % (ct, name) for ct, name in perms))
        return getattr(user_obj, perm_cache_name)

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous():
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = self.get_user_permissions(user_obj, obj)
            user_obj._perm_cache.update(self.get_group_permissions(user_obj, obj))
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm, obj=None):       # obj is project or None
        if not user_obj.is_active:
            return False
        return perm in self.get_all_permissions(user_obj, obj)


def admin_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_active and u.is_superuser,
        login_url='/',               # can not use reverse() in urlconf
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def anonymous_perm(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: anonymous_access() or u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class PermCheckCreateView(CreateView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_active and (user.is_superuser or self.has_perm(request, *args, **kwargs)):
            return super(PermCheckCreateView, self).get(request, *args, **kwargs)
        else:
            return self.no_perm()

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_active and (user.is_superuser or self.has_perm(request, *args, **kwargs)):
            return super(PermCheckCreateView, self).post(request, *args, **kwargs)
        else:
            return self.no_perm()

    def has_perm(self, request, *args, **kwargs):
        return True

    def no_perm(self):
        return no_perm()


class PermCheckUpdateView(UpdateView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_active and (user.is_superuser or self.has_perm(request, *args, **kwargs)):
            return super(PermCheckUpdateView, self).get(request, *args, **kwargs)
        else:
            return self.no_perm()

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_active and (user.is_superuser or self.has_perm(request, *args, **kwargs)):
            return super(PermCheckUpdateView, self).post(request, *args, **kwargs)
        else:
            return self.no_perm()

    def has_perm(self, request, *args, **kwargs):
        return True

    def no_perm(self):
        return no_perm()


class PermCheckListView(ListView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_active and (user.is_superuser or self.has_perm(request, *args, **kwargs)):
            return super(PermCheckListView, self).get(request, *args, **kwargs)
        else:
            return self.no_perm()

    def has_perm(self, request, *args, **kwargs):
        return True

    def no_perm(self):
        return no_perm()


class PermCheckDetailView(DetailView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_active and (user.is_superuser or self.has_perm(request, *args, **kwargs)):
            return super(PermCheckDetailView, self).get(request, *args, **kwargs)
        else:
            return self.no_perm()

    def has_perm(self, request, *args, **kwargs):
        return True

    def no_perm(self):
        return no_perm()


class PermCheckDeleteView(DeleteView):
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_active and (user.is_superuser or self.has_perm(request, *args, **kwargs)):
            return super(PermCheckDeleteView, self).get(request, *args, **kwargs)
        else:
            return self.no_perm()

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_active and (user.is_superuser or self.has_perm(request, *args, **kwargs)):
            return super(PermCheckDeleteView, self).get(request, *args, **kwargs)
        else:
            return self.no_perm()

    def has_perm(self, request, *args, **kwargs):
        return True

    def no_perm(self):
        return no_perm()


class PermCheckView(View):
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_active and (user.is_superuser or self.has_perm(request, *args, **kwargs)):
            return super(PermCheckView, self).dispatch(request, *args, **kwargs)
        else:
            return self.no_perm()

    def has_perm(self, request, *args, **kwargs):
        return True

    def no_perm(self):
        return no_perm()


def no_perm():
    return redirect('status_403')
