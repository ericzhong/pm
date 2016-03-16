from django.views.generic import View
from django.shortcuts import render
from ..models import Setting as SettingModel
from .auth import SuperuserRequiredMixin

_settings = ['app_name',
             'welcome_text',
             'file_size_limit',
             'entries_per_page',
             'text_format',
             'file_display_size_limit']


class Setting(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context['data'] = { n.name: n.value for n in SettingModel.objects.all() }
        return render(request, '_admin/settings.html', context=context)

    def post(self, request, *args, **kwargs):

        if 0 == SettingModel.objects.all().count():
            SettingModel.objects.bulk_create([ SettingModel(name=n, value=request.POST.get(n, '')) for n in _settings ])
        else:
            for n in _settings:
                if n in request.POST:
                    SettingModel.objects.filter(name=n).update(value=request.POST[n])
        context = dict()
        context['data'] = { n.name: n.value for n in SettingModel.objects.all() }
        return render(request, '_admin/settings.html', context=context)


def allow_anonymous_access():
    return True     # TODO: data from settings


def page_size():
    return 3        # TODO
