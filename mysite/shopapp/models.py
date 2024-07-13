from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy
from django_resized import ResizedImageField


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return f"products/product_{instance.pk}/preview/{filename}"


class Product(models.Model):
    """
    Модель представления товаров,
    которые можно выставлять на продажу в интернет-магазине.

    Заказы: :model:`shopapp.Order`
    """
    objects = None
    orders = None

    class Meta:
        ordering = ['name']

    name = models.CharField(verbose_name=gettext_lazy("Название"), max_length=30, db_index=True)
    description = models.TextField(verbose_name=gettext_lazy("Описание"), null=False, blank=True, db_index=True)
    price = models.DecimalField(verbose_name=gettext_lazy("Цена"), default=0, max_digits=8, decimal_places=2)
    discount = models.PositiveSmallIntegerField(verbose_name=gettext_lazy("Процент скидки"), default=0)
    quantity = models.PositiveSmallIntegerField(verbose_name=gettext_lazy("Количество товара"), default=0)
    created_at = models.DateTimeField(verbose_name=gettext_lazy("Время создания"), auto_now_add=True)
    created_by = models.ForeignKey(User, verbose_name=gettext_lazy("Пользователь"), on_delete=models.PROTECT)
    archived = models.BooleanField(default=False)
    preview = ResizedImageField(verbose_name=gettext_lazy("Предпросмотр"), null=True, blank=True,
                                upload_to=product_preview_directory_path)

    def get_absolute_url(self):
        return reverse("shopapp:products_detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"[{self.id}] {gettext_lazy('Продукт')} — {self.name!r}"


def product_images_directory_path(instance: "ProductImage", filename: str):
    return f"products/product_{instance.product.pk}/images/{filename}"


class ProductImage(models.Model):
    objects = None
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = ResizedImageField(verbose_name=gettext_lazy("Изображение"), upload_to=product_images_directory_path)
    description = models.CharField(max_length=100, null=False, blank=True)


class Order(models.Model):
    """
    Модель представления заказов.

    Товары: :model:`shopapp.Product`
    """
    objects = None

    class Meta:
        ordering = ['pk']

    delivery_address = models.TextField(
        verbose_name=gettext_lazy("Адрес доставки"),
        null=False,
        blank=True
    )
    promocode = models.CharField(
        verbose_name=gettext_lazy("Промокод"),
        max_length=20, null=False,
        blank=True,
        default="None"
    )
    created_at = models.DateTimeField(
        verbose_name=gettext_lazy("Время создания"),
        auto_now_add=True
    )
    user = models.ForeignKey(
        User,
        verbose_name=gettext_lazy("Пользователь"),
        on_delete=models.PROTECT,
        related_name="user_orders"
    )
    products = models.ManyToManyField(Product, verbose_name=gettext_lazy("Продукт"), related_name="orders")
    receipt = models.FileField(null=True, upload_to="orders/receipts/")

    def __str__(self) -> str:
        return f"[{self.id}] {gettext_lazy('Заказ')} — {self.delivery_address!r}"
