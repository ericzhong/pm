from django.shortcuts import render
from django.views.generic import View


class homepage(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


