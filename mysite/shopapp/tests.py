import json
from random import choices
from string import ascii_letters

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse
from shopapp.models import Order, Product


class CookieViewTestCase(TestCase):
    def test_get_cookie(self):
        response = self.client.get(reverse('myauth:cookie_get'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'default value')

    def test_set_cookie(self):
        response = self.client.get(reverse('myauth:cookie_set'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies['my_cookie'].value, 'my_value')


class ProductViewTestCase(TestCase):
    fixture = ["fixture.json"]

    def test_product_list_view(self):
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=True).all(),
            values=(pk for pk in response.context['products']),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')
        self.assertContains(response, 'Список продуктов')


class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test_user', password='test_password')
        cls.user.user_permissions.add(Permission.objects.get(codename='add_product'))
        # target_group = Group.objects.get(name='product_manager')
        # cls.user.groups.add(target_group)

    def setUp(self):
        self.client.force_login(self.user)
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_product_create_view(self):
        response = self.client.post(
            reverse('shopapp:products_create'),
            {
                'name': self.product_name,
                'price': '100',
                'description': 'test description',
                'discount': '20'
            }
        )
        self.assertRedirects(response, reverse('shopapp:products_list'))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        cls.user.user_permissions.add(Permission.objects.get(codename='add_product'))

    def setUp(self):
        self.product = Product.objects.create(name='Product Name', price='100', created_by=self.user)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def tearDown(self):
        self.product.delete()

    def test_get_product(self):
        response = self.client.get(reverse('shopapp:products_detail', kwargs={'pk': self.product.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopapp/products-detail.html')
        self.assertContains(response, 'Информация о продукте')
        self.assertContains(response, self.product.name)


class OrderListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_order_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopapp/orders-list.html')
        self.assertContains(response, 'Список заказов')


class OrderDetailViewTestCase(TestCase):
    fixture = ["fixture.json"]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        cls.user.user_permissions.add(Permission.objects.get(codename='view_order'))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.product = Product.objects.create(
            name='Product Name',
            price='100',
            created_by=self.user,
        )
        self.order = Order.objects.create(
            delivery_address="TestStreet",
            user=self.user,
        )
        self.order.products.add(self.product)

    def tearDown(self):
        self.order.delete()
        self.product.delete()

    def test_order_details(self):
        response = self.client.get(reverse('shopapp:orders_detail', kwargs={'pk': self.order.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopapp/orders-detail.html')
        self.assertContains(response, 'Информация о заказе')
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertTrue(response.context['orders'].pk, self.order.pk)


class ProductDataExportViewTestCase(TestCase):
    fixtures = [
        'user-fixture.json',
        'products-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse('shopapp:products_export'))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': str(product.price),
                'archived': product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data['products'], expected_data)


class OrderDataExporterTestCase(TestCase):
    fixtures = [
        'user-fixture.json',
        'products-fixture.json',
        'orders-fixture.json',
    ]

    def test_get_orders_view(self):
        response = self.client.get(reverse('shopapp:orders_export'))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': order.pk,
                'user': order.user.username,
                'delivery_address': order.delivery_address,
                'created_at': order.created_at.strftime('%Y-%m-%d'),
                'promocode': order.promocode,
                'products': [
                    {
                        'pk': product.pk,
                        'name': product.name,
                        'price': str(product.price),
                        'archived': product.archived,
                    }
                    for product in order.products.all()
                ]
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(orders_data['orders'], expected_data)
