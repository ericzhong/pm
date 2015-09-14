# coding:utf-8
from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ["created_on", 'updated_on']

    def clean_identifier(self):
        return self.cleaned_data.get('identifier') or None