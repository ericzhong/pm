#!/usr/bin/env python
# coding:utf-8

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import sys
import inspect
from pm import models

if __name__ == "__main__":

    _pk = ("- model: pm.%s\n"
           "  pk: %s\n"
           "  fields:\n")
    _fd = "    %s: %s\n"
    text = ""

    for item in inspect.getmembers(sys.modules[models.__name__], inspect.isclass):
        cls = item[1]
        tb = item[0].lower()
        if hasattr(cls, '_initial_data'):
            for n in cls._initial_data:
                text += _pk % (tb, n['pk'])
                for key, value in n.iteritems():
                    if key != 'pk':
                        text += _fd % (key, value)

    if text:
        with open('initial_data.yaml', mode='w') as f:
            f.write(text.encode('utf-8'))
