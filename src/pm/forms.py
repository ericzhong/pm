# coding:utf-8
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Group, Permission
from .models import Project, Issue, IssueTag, IssueCategory, IssueStatus, \
    Version, Comment, Worktime, Role, User, Settings
from django.conf import settings
from django.forms import ModelMultipleChoiceField

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


class UpdateProjectForm(ProjectForm):
    class Meta:
        model = Project
        exclude = ['created_on', 'updated_on', 'status', 'users', 'groups', 'created_by']


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

    def clean(self):
        start_date = self.cleaned_data.get('start_date', None)
        due_date = self.cleaned_data.get('due_date', None)
        if start_date and due_date and start_date > due_date:
            raise forms.ValidationError('Due date should be greater than start date')
        return super(IssueForm, self).clean()


class UpdateIssueForm(IssueForm):
    class Meta:
        model = Issue
        exclude = ['created_on', 'updated_on', 'watchers', 'author']


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

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    password1 = forms.CharField(widget=forms.PasswordInput(), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=True)

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email', 'is_superuser']

    def clean(self):
        password1 = self.cleaned_data.get('password1', None)
        password2 = self.cleaned_data.get('password2', None)

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


class UpdateUserForm(UserForm):

    password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False)


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

    class PermissionModelMultipleChoiceField(ModelMultipleChoiceField):
        def label_from_instance(self, obj):
            return obj.name

    permissions = PermissionModelMultipleChoiceField(
        queryset=Permission.objects.filter(content_type__app_label='pm', content_type__model='project').order_by('id'),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        if self.instance.id == Role.ANONYMOUS_ROLE:
            self.fields['permissions'].queryset = Permission.objects.filter(content_type__app_label='pm',
                                                                            content_type__model='project',
                                                                            codename__startswith="read_").order_by('id')

    class Meta:
        model = Role
        fields = ['name', 'permissions']

    def save(self, commit=True):
        role = super(RoleForm, self).save(commit=False)
        role.save()
        self.save_m2m()
        return role


class UserAccountForm(UpdateUserForm):
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


class AllIssuesForm(forms.Form):

    project = forms.ChoiceField()
    version = forms.ChoiceField()
    tag = forms.ChoiceField()
    status = forms.ChoiceField()
    priority = forms.ChoiceField()
    assignee = forms.ChoiceField()
    watcher = forms.ChoiceField()
    start_date = forms.DateField()
    due_date = forms.DateField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)             # pop unexpected args
        super(AllIssuesForm, self).__init__(*args, **kwargs)

        _user_choices = [(str(u.id), str(u)) for u in User.objects.all()]
        from views.project import get_visible_projects
        projects = get_visible_projects(user)
        versions = Version.objects.filter(project__in=projects)
        self.fields['project'].choices = [('', 'All projects')] + [(n.id, n.name) for n in projects]
        self.fields['version'].choices = [('', 'All versions')] + [(n.id, n.name) for n in versions]
        self.fields['tag'].choices = [('', 'All issue tags')] + list(IssueTag.objects.all().values_list('id', 'name'))
        self.fields['status'].choices = [('', 'All issue statuses')] + \
                                        list(IssueStatus.objects.all().values_list('id', 'name')) + \
                                        [(IssueStatus.NOT_CLOSED_STATUS, 'Not closed')]
        self.fields['priority'].choices = [('', 'All priorities')] + list(Issue.PRIORITY_CHOICES)
        self.fields['assignee'].choices = [('', 'All assignees')] + _user_choices
        self.fields['watcher'].choices = [('', 'All watchers')] + _user_choices


class UpdateSettingsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UpdateSettingsForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.iteritems():
            self.fields[key].required = False

    class Meta:
        model = Settings
        exclude = ['']
