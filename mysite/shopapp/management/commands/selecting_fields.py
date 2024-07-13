from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Начата выборка полей")
        user_values = User.objects.values_list("pk", "username")
        for user_value in user_values:
            print(user_value)

        product_values = Product.objects.values("pk", "name")
        for product_value in product_values:
            print(product_value)
        self.stdout.write(self.style.SUCCESS(f"Выполнено"))
