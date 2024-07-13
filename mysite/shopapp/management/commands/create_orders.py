from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from shopapp.models import Order, Product
from django.db import transaction
from typing import Sequence


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        user = User.objects.get(username="admin")
        # products: Sequence[Product] = Product.objects.defer("description", "price", "created_at").all()
        products: Sequence[Product] = Product.objects.only("id").all()
        order, created = Order.objects.get_or_create(
            delivery_address="123 Main St",
            promocode="123456",
            user=user,

        )
        for product in products:
            order.products.add(product)
        order.save()
        self.stdout.write(self.style.SUCCESS(f"Заказ успешно создан {order}"))
        self.stdout.write(self.style.SUCCESS("База данных магазина заказов (Order) успешно создана."))
