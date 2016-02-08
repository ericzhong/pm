from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
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
        if not user_obj.is_active or user_obj.is_anonymous() or obj is not None:
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
