from django.shortcuts import render
from django.views.generic import View
from django.contrib import messages
from .auth import AnonPermMixin

create_success_message = '%s was created successfully.'
update_success_message = '%s was updated successfully.'
delete_success_message = '%s was deleted successfully.'


class homepage(AnonPermMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


def decorate_object(obj):
    return '\"%s\"' % obj


class SuccessMessageMixin(object):
    success_message = ''

    def form_valid(self, form):
        response = super(SuccessMessageMixin, self).form_valid(form)
        success_message = self.get_success_message()
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self):
        return self.success_message


class CreateSuccessMessageMixin(SuccessMessageMixin):
    def get_success_message(self):
        return self.success_message or create_success_message % decorate_object(self.object)


class UpdateSuccessMessageMixin(SuccessMessageMixin):
    def get_success_message(self):
        return self.success_message or update_success_message % decorate_object(self.object)


class DeleteSuccessMessageMixin(object):
    def delete(self, request, *args, **kwargs):
        success_message = self.get_success_message()
        if success_message:
            messages.success(self.request, success_message)

        return super(DeleteSuccessMessageMixin, self).delete(request, *args, **kwargs)

    def get_success_message(self):
        return delete_success_message % decorate_object(self.get_object())
