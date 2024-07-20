from django import forms
from django.contrib.auth.models import User

from django.utils.translation import gettext_lazy


class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(label=gettext_lazy("Имя пользователя"), max_length=40, required=True)
    first_name = forms.CharField(label=gettext_lazy("Имя"), max_length=30, required=True)
    last_name = forms.CharField(label=gettext_lazy("Фамилия"), max_length=30, required=True)
    email = forms.EmailField(label=gettext_lazy("Почта"), required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]

    bio = forms.CharField(label="О себе", max_length=500, widget=forms.Textarea(attrs={'rows': 8, 'cols': 50}))
    avatar = forms.ImageField(label="Аватар", required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        if self.instance.profile_user:
            self.fields['bio'].initial = self.instance.profile_user.bio
            self.fields['avatar'].initial = self.instance.profile_user.avatar

    def clean(self):
        email = self.cleaned_data['email']
        if email == "" or self.instance.email == email:
            return

        if User.objects.filter(email=email).exists():
            return self.add_error("email", gettext_lazy("Эта почта уже занята"))

    def save(self, commit=True):
        user = super(ProfileEditForm, self).save(commit=False)
        profile = user.profile_user
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        profile.bio = self.cleaned_data['bio']
        user.save()
        profile.avatar = self.cleaned_data['avatar']
        if commit:
            user.save()
            profile.save()
        return profile
