# Generated by Django 5.0.3 on 2024-06-21 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myauth", "0002_profile_avatar"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="bio",
            field=models.TextField(
                blank=True, max_length=300, null=True, verbose_name="О себе"
            ),
        ),
    ]
