from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        products_name = [
            "Laptop",
            "Desktop",
            "Smartphone",
            "Smartlink"
        ]

        user = User.objects.get(pk=1)
        for product_name in products_name:
            product, created = Product.objects.get_or_create(name=product_name, created_by=user)
            self.stdout.write(self.style.SUCCESS(f"Создан продукт: {product.name}"))

        self.stdout.write(self.style.SUCCESS("База данных магазина продуктов (Product) успешно создана."))
