from django.views.generic import View
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.shortcuts import render
from ..forms import UserAccountForm, UploadAvatarForm
from ..models import Profile
from .base import UpdateSuccessMessageMixin, update_success_message
from .auth import UserPermMixin
from django.conf import settings
import os
from PIL import Image


class MyAccount(UserPermMixin, UpdateSuccessMessageMixin, UpdateView):
    model = User
    form_class = UserAccountForm
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self, queryset=None):
        return self.request.user


class MyAvatar(UserPermMixin, View):

    _AVATAR_MAX_WIDTH = 100
    _AVATAR_MAX_HEIGHT = 100

    def get(self, request, *args, **kwargs):
        form = UploadAvatarForm()
        return render(request, 'avatar.html', {'form': form})

    def handle_uploaded_file(self, f, name):
        ext = name.split(".")[-1].lower()
        new_name = '%s.%s' % (self.request.user.id, ext)
        dir = settings.UPLOAD_AVATAR_DIR
        path = os.path.join(dir, new_name)

        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(path, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
                dest.close()

        im = Image.open(path)
        width,height = im.size
        if width > self._AVATAR_MAX_WIDTH or height > self._AVATAR_MAX_HEIGHT:
            im.resize((self._AVATAR_MAX_WIDTH, self._AVATAR_MAX_HEIGHT)).save(path)

        p = Profile.objects.get_or_create(user=self.request.user)[0]
        p.avatar = new_name
        p.save()

    def post(self, request, *args, **kwargs):
        form = UploadAvatarForm(request.POST, request.FILES)
        if form.is_valid():
            self.handle_uploaded_file(request.FILES['file'], form.cleaned_data['file'].name)

            from django.contrib import messages
            messages.success(self.request, update_success_message % 'avatar')
        return render(request, 'avatar.html', {'form': form})
