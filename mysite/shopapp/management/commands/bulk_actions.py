from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Начата запись массовых данных")
        data = [
            ("Smartphone 1", 12000),
            ("Smartphone 2", 16000),
            ("Smartphone 3", 22000),
        ]
        user = User.objects.get(pk=1)
        products = [
            Product(name=name, price=price, created_by=user)
            for name, price in data
        ]

        result = Product.objects.bulk_create(products)

        for obj in result:
            print(obj)
        self.stdout.write(self.style.SUCCESS("Выполнено"))
