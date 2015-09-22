# coding:utf-8
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Group
from .models import Project, Issue, IssueType, IssueStatus, Version, Member


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ["created_on", 'updated_on']

    def clean_identifier(self):
        return self.cleaned_data.get('identifier') or None    # for "null=True, blank=True, unique=True"


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        exclude = ["created_on", 'updated_on']


class IssueTypeForm(forms.ModelForm):
    class Meta:
        model = IssueType
        exclude = ['']


class IssueStatusForm(forms.ModelForm):
    class Meta:
        model = IssueStatus
        exclude = ['']


class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        exclude = ["created_on", 'updated_on']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ["password", "date_joined", 'last_login']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = [""]


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = ["created_on"]



class PasswordResetByEmailForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("This email is invalid.")

        return email