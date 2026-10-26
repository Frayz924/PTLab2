from django.test import TestCase, Client
from shop.models import Product, CartItem


class CartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product1 = Product.objects.create(name='Вино', price=1000)
        self.product2 = Product.objects.create(name='Пиво', price=200)

    def test_add_product_to_cart(self):
        """Добавление товара создаёт позицию с quantity=1."""
        self.client.get(f'/cart/add/{self.product1.id}/')
        item = CartItem.objects.get(product=self.product1)
        self.assertEqual(item.quantity, 1)

    def test_add_same_product_twice_increments_quantity(self):
        """Повторное добавление того же товара увеличивает quantity (вариант 5)."""
        self.client.get(f'/cart/add/{self.product1.id}/')
        self.client.get(f'/cart/add/{self.product1.id}/')
        item = CartItem.objects.get(product=self.product1)
        self.assertEqual(item.quantity, 2)

    def test_add_different_products_creates_separate_items(self):
        """Разные товары — разные позиции в корзине."""
        self.client.get(f'/cart/add/{self.product1.id}/')
        self.client.get(f'/cart/add/{self.product2.id}/')
        self.assertEqual(CartItem.objects.count(), 2)

    def test_cart_detail_total_quantity(self):
        """Общее количество = сумма quantity всех позиций."""
        self.client.get(f'/cart/add/{self.product1.id}/')
        self.client.get(f'/cart/add/{self.product1.id}/')
        self.client.get(f'/cart/add/{self.product2.id}/')
        response = self.client.get('/cart/')
        self.assertEqual(response.context['total_quantity'], 3)

    def test_cart_detail_empty(self):
        """Пустая корзина отображается корректно."""
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_quantity'], 0)
        self.assertEqual(len(response.context['items']), 0)

    def test_remove_from_cart(self):
        """Удаление позиции убирает её из корзины."""
        self.client.get(f'/cart/add/{self.product1.id}/')
        item = CartItem.objects.get(product=self.product1)
        self.client.get(f'/cart/remove/{item.id}/')
        self.assertEqual(CartItem.objects.count(), 0)

    def test_cart_isolated_between_sessions(self):
        """Корзина разных сессий не смешивается."""
        self.client.get(f'/cart/add/{self.product1.id}/')
        other_client = Client()
        other_client.get(f'/cart/add/{self.product2.id}/')
        # У первого клиента — только product1
        first_items = CartItem.objects.filter(product=self.product1)
        self.assertEqual(first_items.count(), 1)
        second_items = CartItem.objects.filter(product=self.product2)
        self.assertEqual(second_items.count(), 1)