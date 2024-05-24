from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторіть пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name','email')

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Email already in use.')
        return data

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo', 'about')


class AccessRequestForm(forms.Form):
    access_types = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Виберіть доступ'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            all_access_choices = [
                ('article', 'Створювати статті'),
                ('course', 'Створювати курси')
            ]
            missing_permissions = []
            if not user.groups.filter(name='Articles Admins').exists():
                missing_permissions.append(('article', 'Створювати статті'))
            if not user.groups.filter(name='Course Admins').exists():
                missing_permissions.append(('course', 'Створювати курси'))
            self.fields['access_types'].choices = missing_permissions