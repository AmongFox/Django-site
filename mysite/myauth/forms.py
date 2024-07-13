from django import forms
from django.contrib.auth.models import User

from .models import Profile
from django.utils.translation import gettext_lazy


class ProfileEditForm(forms.ModelForm):
    bio = forms.CharField(label="О себе", max_length=500, widget=forms.Textarea(attrs={'rows': 8, 'cols': 50}))

    class Meta:
        model = Profile
        fields = [
            "bio",
            "avatar",
        ]

    user_username = forms.CharField(label=gettext_lazy("Имя пользователя"), max_length=40, required=True)
    user_first_name = forms.CharField(label=gettext_lazy("Имя"), max_length=30, required=True)
    user_last_name = forms.CharField(label=gettext_lazy("Фамилия"), max_length=30, required=True)
    user_email = forms.EmailField(label=gettext_lazy("Почта"), required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['user_username'].initial = self.instance.user.username
            self.fields['user_first_name'].initial = self.instance.user.first_name
            self.fields['user_last_name'].initial = self.instance.user.last_name
            self.fields['user_email'].initial = self.instance.user.email

    def clean(self):
        email = self.cleaned_data['user_email']
        if email == "" or self.fields['user_email'].initial == email:
            return

        if User.objects.filter(email=email).exists():
            return self.add_error("user_email", gettext_lazy("Эта почта уже занята"))

    def save(self, commit=True):
        profile = super(ProfileEditForm, self).save(commit=False)
        user = profile.user
        user.username = self.cleaned_data['user_username']
        user.first_name = self.cleaned_data['user_first_name']
        user.last_name = self.cleaned_data['user_last_name']
        user.email = self.cleaned_data['user_email']
        if commit:
            user.save()
            profile.save()
        return profile
