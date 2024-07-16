from django import forms
from django.contrib.auth.models import User

from .models import Profile
from django.utils.translation import gettext_lazy


class ProfileEditForm(forms.ModelForm):
    bio = forms.CharField(
        label=gettext_lazy("О себе"),
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 8, 'cols': 50}),
        required=False
    )
    avatar = forms.ImageField(label=gettext_lazy("Аватар"), required=False)

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
        if self.instance:
            self.fields['user_username'].initial = self.instance.username
            self.fields['user_first_name'].initial = self.instance.first_name
            self.fields['user_last_name'].initial = self.instance.last_name
            self.fields['user_email'].initial = self.instance.email

    def clean(self):
        email = self.cleaned_data['user_email']
        if email == "" or self.fields['user_email'].initial == email:
            return

        if User.objects.filter(email=email).exists():
            return self.add_error("user_email", gettext_lazy("Эта почта уже занята"))

    def save(self, commit=True):
        user = super(ProfileEditForm, self).save(commit=False)
        profile = user.profile_user
        user.username = self.cleaned_data['user_username']
        user.first_name = self.cleaned_data['user_first_name']
        user.last_name = self.cleaned_data['user_last_name']
        user.email = self.cleaned_data['user_email']
        if commit:
            user.save()
            profile.save()
        return profile
