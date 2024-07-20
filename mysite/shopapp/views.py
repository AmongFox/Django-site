"""
Наборы представлений интернет-магазина по товарам и заказам.
"""
from csv import DictWriter
from timeit import default_timer
import logging

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.contrib.gis.feeds import Feed
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, reverse, get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from .forms import GroupForm, OrderForm, ProductCreateForm, ProductUpdateForm
from .models import Order, Product, ProductImage
from .serializers import ProductSerializer, OrderSerializer


logger = logging.getLogger(__name__)


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ("Laptop", 2000),
            ("desktop", 4000),
            ("smartphone", 982),
            ("Smartlink", 1920)
        ]

        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 2,
        }
        logger.debug("Продукты для индекса магазина: %s", products)
        logger.info("Рендеринг индексов магазина")
        return render(request, "shopapp/shop-index.html", context=context)


class GroupListView(ListView):
    """
    Класс отображения групп
    template_name: String - Шаблон отрисовки HTML кода
    model: Class[models.Model] - Модель описания данных
    context_object_name: String - Имя переменной в шаблоне
    """
    template_name = 'shopapp/groups-list.html'
    model = Group
    context_object_name = "groups"


class ProductListView(ListView):
    """
    Класс отображения продуктов
    template_name: String - Шаблон отрисовки HTML кода
    queryset: Class - Передает значение archived=False, что прекращает отображения продуктов с таким флагом
    context_object_name: String - Имя переменной в шаблоне
    """
    template_name = "shopapp/products-list.html"
    queryset = Product.objects.filter(archived=False)
    context_object_name = "products"


class GroupCreateView(PermissionRequiredMixin, CreateView):
    # permission_required =
    """
    Класс создания групп
    template_name: String - Шаблон отрисовки HTML кода
    model: Class[models.Model] - Модель описания данных
    form_class: Class - Модель заполнения данных в форме
    success_url: String(urls.py) - Ссылка для перехода после создания
    """
    template_name = 'shopapp/groups-create.html'
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy('shopapp:groups_list')


class LatestProductsView(Feed):
    title = "Последние продукты"
    description = "Последние добавленные товары в магазине"
    link = reverse_lazy('shopapp:products_list')

    def items(self):
        return Product.objects.filter(archived=False).sort_by("-created_at")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description[:100] + "..."


class ProductCreateView(PermissionRequiredMixin, CreateView):
    """
    Класс создания продуктов
    template_name: String - Шаблон отрисовки HTML кода
    permission_required: List[<PermissionRequired>] - Предоставляет доступ только тем, у кого есть данные разрешения
    model: Class[models.Model] - Модель описания данных
    form_class: Class - Модель заполнения данных в форме
    success_url: String(urls.py) - Ссылка для перехода после создания
    """
    template_name = "shopapp/products-create.html"
    permission_required = "shopapp.add_product"
    model = Product
    form_class = ProductCreateForm
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form) -> HttpResponse:
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        return response


class ProductDetailView(DetailView):
    """
    Класс просмотра подробностей о продукте
    template_name: String - Шаблон отрисовки HTML кода
    model: Class[models.Model] - Модель описания данных
    context_object_name: String - Имя переменной в шаблоне
    """
    template_name = "shopapp/products-detail.html"
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Класс редактирования продукта
    template_name: String - Шаблон отрисовки HTML кода
    model: Class[models.Model] - Модель описания данных
    form_class: Class - Модель заполнения данных в форме

    Functions:
        get_success_url(pk) -> HttpResponseRedirect
            :parameter (int): pk - Получает уникальное значение продукта для создания ссылки
            Генерирует ссылку для перехода после изменения
    """
    template_name = "shopapp/products-edit.html"
    permission_required = "shopapp.change_product"
    model = Product
    form_class = ProductUpdateForm

    def has_permission(self):
        if self.get_object().created_by_id == self.request.user.pk or self.request.user.is_superuser:
            return True

    def get_success_url(self):
        return reverse(
            'shopapp:products_detail', kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Класс внесения продукта в архив
    template_name: String - Шаблон отрисовки HTML кода
    model: Class[models.Model] - Модель описания данных
    success_url: String - Ссылка для перехода после удаления

    Functions:
        form_valid(form) -> HttpResponseRedirect
            :parameter (Class): form - Принимает объект продукта
            Изменяет параметр archived перенося продукт в архив.
    """
    template_name = "shopapp/products-delete.html"
    permission_required = "shopapp.delete_product"
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,

                }
                for product in products
            ]
        cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})


@extend_schema(description="Просмотр продуктов CRUD")
class ProductSetView(ModelViewSet):
    """
    Класс набора представлений для использования Product
    имеется CRUD сущностей товара
    template_name: String - Шаблон отрисовки HTML кода
    model: Class[models.Model] - Модель описания данных
    context_object_name: String - Имя переменной в шаблоне
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        "name",
        "description",
    ]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @method_decorator(cache_page(120))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Выдача одного продукта по ID",
        description="Извлекает продукт. Возвращает 404, если не найден",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Пустой ответ, товар по идентификатору не найден")
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
            "quantity",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response


class OrderListView(LoginRequiredMixin, ListView):
    """
    Класс отображения заказов
    template_name: String - Шаблон отрисовки HTML кода
    queryset: Tuple[Class] - Достает из базы данных заказы со связями на их пользователя и продукты
    context_object_name: String - Имя переменной в шаблоне
    """
    template_name = "shopapp/orders-list.html"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = "orders"


class UserOrdersListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "shopapp/orders-user-orders.html"
    model = Order
    context_object_name = "orders"

    def __init__(self):
        super().__init__()
        self.owner = None

    def get_queryset(self):
        self.owner = get_object_or_404(User, pk=self.kwargs.get("pk"))
        return super().get_queryset().filter(user=self.owner).prefetch_related("products")

    def has_permission(self):
        if self.kwargs.get("pk") != self.request.user.pk:
            raise PermissionDenied("Нет доступа")
        return True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.owner
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    """
    Класс создания заказов
    template_name: String - Шаблон отрисовки HTML кода
    model: Class[models.Model] - Модель описания данных
    form_class: Class - Модель заполнения данных в форме
    success_url: String(urls.py) - Ссылка для перехода после создания
    """
    template_name = "shopapp/orders-create.html"
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('shopapp:orders_list')


class OrderDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Класс просмотра подробностей о заказе
    template_name: String - Шаблон отрисовки HTML кода
    queryset: Tuple[Class] - Достает из базы данных заказы со связями на их пользователя и продукты
    context_object_name: String - Имя переменной в шаблоне
    """
    template_name = "shopapp/orders-detail.html"
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = "orders"


class OrderUpdateView(UpdateView):
    """
    Класс редактирования продукта
    template_name: String - Шаблон отрисовки HTML кода
    model: Class[models.Model] - Модель описания данных
    form_class: Class - Модель заполнения данных в форме

    Functions:
        get_success_url(pk) -> HttpResponseRedirect
            :parameter (int): pk - Получает уникальное значение продукта для создания ссылки
            Генерирует ссылку для перехода после изменения
    """
    template_name = "shopapp/orders-edit.html"
    model = Order
    form_class = OrderForm

    def get_success_url(self):
        return reverse(
            'shopapp:orders_detail', kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    """
    Класс внесения продукта в архив
    template_name: String - Шаблон отрисовки HTML кода
    model: Class[models.Model] - Модель описания данных
    success_url: String - Ссылка для перехода после удаления
    """
    template_name = "shopapp/orders-delete.html"
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class OrderDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "user": order.user.username,
                "delivery_address": order.delivery_address,
                "created_at": order.created_at.strftime("%Y-%m-%d"),
                "promocode": order.promocode,
                "products": [
                    {
                        "pk": product.pk,
                        "name": product.name,
                        "price": product.price,
                        "archived": product.archived,
                    }
                    for product in order.products.all()
                ]
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class UserOrdersDataExportView(View):
    def get(self, request: HttpRequest, pk: int) -> JsonResponse:
        cache_key = f"users_orders_export_{pk}"
        orders_data = cache.get(cache_key)
        if orders_data is None:
            user = get_object_or_404(User, pk=pk)
            orders = Order.objects.filter(user=user).order_by("pk").all()
            orders_data = [
                {
                    "pk": order.pk,
                    "user": order.user.username,
                    "delivery_address": order.delivery_address,
                    "created_at": order.created_at.strftime("%Y-%m-%d"),
                    "promocode": order.promocode,
                    "products": [
                        {
                            "pk": product.pk,
                            "name": product.name,
                            "price": product.price,
                            "archived": product.archived,
                        }
                        for product in order.products.all()
                    ]
                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 300)
        return JsonResponse({"orders": orders_data})


class OrderSetView(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        "delivery_address",
        "promocode",
    ]
    filterset_fields = [
        "delivery_address",
        "promocode",
    ]
    ordering_fields = [
        "created_at",
    ]
