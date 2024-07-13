from django.urls import path, include
from django.views.decorators.cache import cache_page

from rest_framework.routers import DefaultRouter

from .views import (
    GroupCreateView,
    GroupListView,
    OrderCreateView,
    OrderDataExportView,
    OrderDeleteView,
    OrderDetailView,
    OrderListView,
    UserOrdersListView,
    OrderUpdateView,
    ProductCreateView,
    ProductDataExportView,
    ProductDeleteView,
    ProductDetailView,
    ProductListView,
    ProductUpdateView,
    ProductSetView,
    ShopIndexView,
    OrderSetView,
    LatestProductsView,
    UserOrdersDataExportView,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductSetView)
routers.register("orders", OrderSetView)

urlpatterns = [
    path("", cache_page(0)(ShopIndexView.as_view()), name="index"),

    path("groups/", GroupListView.as_view(), name="groups_list"),
    path("groups/create/", GroupCreateView.as_view(), name="groups_create"),

    path("products/", ProductListView.as_view(), name="products_list"),
    path("products/latest/feed", LatestProductsView(), name="latest_products"),
    path("products/export/", ProductDataExportView.as_view(), name="products_export"),
    path("products/create/", ProductCreateView.as_view(), name="products_create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="products_detail"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="products_update"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="products_delete"),

    path("orders/", OrderListView.as_view(), name="orders_list"),
    path("orders/export/", OrderDataExportView.as_view(), name="orders_export"),
    path("orders/create/", OrderCreateView.as_view(), name="orders_create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="orders_detail"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="orders_update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="orders_delete"),

    path("user/<int:pk>/orders/", UserOrdersListView.as_view(), name="user_orders"),
    path("user/<int:pk>/orders/export/", UserOrdersDataExportView.as_view(), name="user_orders"),

    path("api/", include(routers.urls)),
]
