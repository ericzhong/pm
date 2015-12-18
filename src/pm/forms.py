# coding:utf-8
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from .models import Project, Issue, IssueTag, IssueCategory, IssueStatus, Version, Member, Comment, Worktime


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['created_on', 'updated_on', 'status', 'members', 'groups']

    def clean_identifier(self):
        return self.cleaned_data.get('identifier') or None    # for 'null=True, blank=True, unique=True'


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        exclude = ['created_on', 'updated_on']


class IssueCategoryForm(forms.ModelForm):
    class Meta:
        model = IssueCategory
        exclude = ['project']


class IssueTagForm(forms.ModelForm):
    class Meta:
        model = IssueTag
        exclude = ['']


class IssueStatusForm(forms.ModelForm):
    class Meta:
        model = IssueStatus
        exclude = ['']


class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        exclude = ['created_on', 'updated_on']


class UserForm(forms.ModelForm):

    password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        exclude = ['password', 'date_joined', 'last_login']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError('two different passwords')
            else:
                cleaned_data['password'] = make_password(cleaned_data.get('password1'))

        return cleaned_data

    def save(self, commit=True):
        instance = super(UserForm, self).save(commit=False)
        instance.password = self.cleaned_data.get('password', '')

        if commit:
            instance.save()

        return instance


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ['']


class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        exclude = ['created_on']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class WorktimeForm(forms.ModelForm):
    class Meta:
        model = Worktime
        exclude = ['created_on', 'updated_on']


class PasswordResetByEmailForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError('This email is invalid.')

        return email