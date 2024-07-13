from django.core.management.base import BaseCommand
from shopapp.models import Product, Order
from django.db.models import Avg, Min, Max, Count, Sum


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Начата агрегация")
        result = Product.objects.filter(
            name__contains="Smartphone"
        ).aggregate(
            Avg("price"),
            max_price=Min("price"),
            min_price=Max("price"),
            count=Count("id"),
        )
        print(result)

        orders = Order.objects.annotate(
            total=Sum("products__price", default=0),
            products_count=Count("products"),
        )
        for order in orders:
            print(f"Заказ {order.pk}: Итого {order.total}, Количество продуктов {order.products_count}")
        self.stdout.write(self.style.SUCCESS("Выполнено"))
