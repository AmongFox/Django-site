from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile


class UserBioForm(forms.Form):
    name = forms.CharField(max_length=40)
    age = forms.IntegerField(label="Возраст", min_value=1, max_value=100)
    bio = forms.CharField(label="Биография", widget=forms.Textarea)


def validate_file_name(file: InMemoryUploadedFile) -> None:
    if file.name and "virus" in file.name:
        raise ValidationError("Файл содержит вирус")


class UploadFileForm(forms.Form):
    file = forms.FileField(label="Выберите файл для загрузки", validators=[
        validate_file_name,
    ])
