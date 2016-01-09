# coding:utf-8
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Group
from .models import Project, Issue, IssueTag, IssueCategory, IssueStatus, Version, Comment, Worktime, Role
from django.conf import settings


_EMPTY_LABEL = ''


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['created_on', 'updated_on', 'status', 'users', 'groups']

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['parent'].empty_label = _EMPTY_LABEL
        if self.instance:       # update
            child = Project.objects.filter(parent=self.instance).values_list('id', flat=True)
            self.fields['parent'].queryset = Project.objects.exclude(id=self.instance.id).exclude(id__in=child)
        return

    def clean_identifier(self):
        return self.cleaned_data.get('identifier') or None    # for 'null=True, blank=True, unique=True'


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        exclude = ['created_on', 'updated_on', 'watchers']

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        for n in ['tag', 'status']:
            self.fields[n].empty_label = None

        for n in ['parent', 'assigned_to', 'version']:
            self.fields[n].empty_label = _EMPTY_LABEL
        return


class IssueCategoryForm(forms.ModelForm):
    class Meta:
        model = IssueCategory
        exclude = ['']


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
        fields = ['username', 'last_name', 'first_name', 'email', 'is_superuser']

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError('two different passwords')
            else:
                self.cleaned_data['password'] = self.cleaned_data['password1']

        return super(UserForm, self).clean()

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        password = self.cleaned_data.get('password', None)
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ['']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class CommentBlankForm(CommentForm):
    def __init__(self, *args, **kwargs):
        super(CommentBlankForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.iteritems():
            self.fields[key].required = False


class WorktimeForm(forms.ModelForm):
    class Meta:
        model = Worktime
        exclude = ['created_on', 'updated_on']


class WorktimeBlankForm(WorktimeForm):
    def __init__(self, *args, **kwargs):
        super(WorktimeBlankForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.iteritems():
            self.fields[key].required = False


class PasswordResetByEmailForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError('This email is invalid.')

        return email


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name']


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UploadAvatarForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        size = self.files['file'].size
        mime = self.files['file'].content_type.split('/')[-1].lower()

        if size > settings.UPLOAD_AVATAR_MAX_SIZE * 1024:      # KB
            raise forms.ValidationError('Upload size limit %sKB' % settings.UPLOAD_AVATAR_MAX_SIZE)

        if mime not in settings.UPLOAD_AVATAR_MIME_TYPES:
            raise forms.ValidationError('Upload format limit %s' % ','.join(settings.UPLOAD_AVATAR_MIME_TYPES))

        return self.cleaned_data['file']