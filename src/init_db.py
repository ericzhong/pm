#!/usr/bin/env python
# coding:utf-8

import os
import django


if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()

    from pm.models import IssueTag, IssueStatus, Role, Permission, Settings

    for cls in IssueStatus, IssueTag:
        for item in cls.INITIAL_DATA:
            cls(id=item[0], name=item[1]).save()

    for item in Role.INITIAL_DATA:
        r = Role(id=item[0], name=item[1])
        r.save()
        if len(item[2]) > 0:
            perms = Permission.objects.filter(codename__in=item[2])
            if perms:
                r.permissions.add(*perms)

    Settings(id=1).save()
