# coding:utf-8
from django import forms
from .models import Project,Issue

'''
class ProjectForm(forms.ModelForm):

    password1 = forms.CharField(widget=forms.PasswordInput(), error_messages=err_1)
    password2 = forms.CharField(widget=forms.PasswordInput(), error_messages=err_2)

    class Meta:
        model = Projects
        fields = ('name',)
        error_messages = {
            'name': {
                'required': "用户名不能为空",
                'unique': "该用户已经存在",
            },
        }

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()

        name = cleaned_data.get('name')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("密码不相同")

        return cleaned_data

'''