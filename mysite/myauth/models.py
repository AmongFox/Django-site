from django.contrib.auth.models import User
from django.db import models
from django_resized import ResizedImageField


def product_preview_directory_path(instance: "Profile", filename: str) -> str:
    return f"users/profile_{instance.pk}/avatar/{filename}"


class Profile(models.Model):
    objects = None
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile_user")
    bio = models.TextField(verbose_name="О себе", max_length=300, null=True, blank=True)
    agreement = models.BooleanField(default=False)
    avatar = ResizedImageField(verbose_name="Аватар пользователя", null=True, blank=True,
                               upload_to=product_preview_directory_path)
