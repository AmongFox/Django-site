from csv import DictReader
from io import TextIOWrapper

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .admin_mixins import ColoredText, ExportAsCSVFile, ExportAsJSONFile
from .models import Order, Product, ProductImage
from .forms import CSVImportForm


class OrderInline(admin.StackedInline):
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = Order.products.through


class ProductImagesInline(admin.StackedInline):
    model = ProductImage


@admin.action(description="Archiving product")
def mark_archived(model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchiving product")
def mark_unarchived(model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVFile, ExportAsJSONFile, ColoredText):
    change_list_template = "shopapp/admin-products-changelist.html"
    actions = [
        mark_archived,
        mark_unarchived,
        "export_as_csv",
        "export_as_json",
        "export_selected_objects",
    ]
    inlines = [
        OrderInline,
        ProductImagesInline,
    ]

    list_display = "product_colored_id", "colored_name", "colored_short_description", "colored_price", "archived"
    list_display_links = "product_colored_id", "colored_name"
    ordering = "id", "name", "price"
    search_fields = "id", "name", "description"
    fieldsets = [
        (None, {
            "fields": ("name", "description",)}),

        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse"),
        }),

        ("Images", {
            "fields": ("preview", ),
        }),

        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options"
        })
    ]

    def import_csv(self, request) -> HttpResponse:
        products = list()
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)
        csv_file = TextIOWrapper(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )

        reader = DictReader(csv_file)
        for row in reader:
            order_data = {
                "name": row['name'],
                "description": row['description'],
                "price": row['price'],
                "discount": row['discount'],
                "created_by": User.objects.get(id=int(row['user'])),
            }
            product = Product(**order_data)
            products.append(product)
        Product.objects.bulk_create(products)
        self.message_user(request, "Товары успешно импортированы")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-products-csv/", self.import_csv, name="import_products_csv"),
        ]
        return my_urls + urls


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ExportAsCSVFile, ExportAsJSONFile, ColoredText):
    change_list_template = "shopapp/admin-orders-changelist.html"
    actions = [
        "export_as_csv",
        "export_as_json",
        ]
    inlines = [
        ProductInline,
    ]

    list_display = "order_colored_id", "colored_delivery_address", "promocode", "created_at", "user_verbose"
    list_display_links = "order_colored_id", "colored_delivery_address", "user_verbose"
    ordering = "id", "delivery_address"
    search_fields = "id", "delivery_address"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)
        csv_file = TextIOWrapper(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )

        reader = DictReader(csv_file)
        for row in reader:
            order_data = {
                "delivery_address": row['delivery_address'],
                "promocode": row['promocode'],
                "user": User.objects.get(id=int(row['user'])),
            }
            products = [Product.objects.get(id=int(product_id)) for product_id in (row['product'].split(','))]
            print(order_data)
            for product in products:
                print(product)
            order = Order(**order_data)
            order.save()
            order.products.add(*products)
        self.message_user(request, "Заказы успешно импортированы")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-orders-csv/", self.import_csv, name="import_orders_csv"),
        ]
        return my_urls + urls
