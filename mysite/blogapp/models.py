from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy
from django.contrib.auth.models import User


class Author(models.Model):
    objects = None
    name = models.CharField(verbose_name=gettext_lazy("Имя"), max_length=100, null=False)
    bio = models.TextField(verbose_name=gettext_lazy("Биография"), blank=True)

    def __str__(self) -> str:
        return f"[{self.id}] {gettext_lazy('Автор')} — {self.name!r}"


class Category(models.Model):
    objects = None
    name = models.CharField(verbose_name=gettext_lazy("Название"), max_length=40)

    def __str__(self) -> str:
        return f"[{self.id}] {gettext_lazy('Категория')} — {self.name!r}"


class Tag(models.Model):
    objects = None
    name = models.CharField(verbose_name=gettext_lazy("Название"), max_length=20)

    def __str__(self) -> str:
        return f"[{self.id}] {gettext_lazy('Тег')} — {self.name!r}"


class Article(models.Model):
    objects = None
    title = models.CharField(verbose_name=gettext_lazy("Заголовок"), max_length=200)
    content = models.TextField(verbose_name=gettext_lazy("Содержание"))
    pub_date = models.DateTimeField(verbose_name=gettext_lazy("Дата создания"), auto_now_add=True)
    author = models.ForeignKey(
        Author,
        verbose_name=gettext_lazy("Автор"),
        on_delete=models.CASCADE,
        related_name="articles",
    )
    category = models.ForeignKey(
        Category,
        verbose_name=gettext_lazy("Категория"),
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=gettext_lazy("Теги")
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=gettext_lazy("Создатель"),
        on_delete=models.CASCADE,
        related_name="articles",
    )

    def get_absolute_url(self):
        return reverse("blogapp:article_detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"[{self.id}] {gettext_lazy('Статья')} — {self.title!r}"
