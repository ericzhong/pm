from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator



class homepage(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')
