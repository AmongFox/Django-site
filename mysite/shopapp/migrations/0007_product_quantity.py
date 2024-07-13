# Generated by Django 5.0.3 on 2024-06-21 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0006_alter_product_preview_alter_productimage_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="quantity",
            field=models.PositiveSmallIntegerField(
                default=0, verbose_name="Количество товара"
            ),
        ),
    ]
