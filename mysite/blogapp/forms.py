from django import forms

from .models import Author, Category, Tag, Article
from django.utils.translation import gettext_lazy


class AuthorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True

    class Meta:
        model = Author
        fields = [
            "name",
            "bio",
        ]


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True

    class Meta:
        model = Category
        fields = [
            "name",
        ]


class TagForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True

    class Meta:
        model = Tag
        fields = [
            "name",
        ]


class ArticleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["content"].required = True

    class Meta:
        model = Article
        fields = [
            "title",
            "content",
            "author",
            "category",
            "tags",
            "created_by",
        ]
