from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, StockTransaction


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Wireless Mouse",
            sku="ELEC-001",
            category=self.category,
            price=799,
            quantity=5,
            reorder_level=10,
        )

    def test_is_low_stock_true_when_at_or_below_reorder_level(self):
        self.assertTrue(self.product.is_low_stock)

    def test_is_low_stock_false_when_above_reorder_level(self):
        self.product.quantity = 50
        self.assertFalse(self.product.is_low_stock)

    def test_str_includes_name_and_sku(self):
        self.assertEqual(str(self.product), "Wireless Mouse (ELEC-001)")


class StockAdjustViewTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="USB-C Cable", sku="ELEC-002", price=299, quantity=10
        )
        self.url = reverse("stock_adjust", args=[self.product.pk])

    def test_stock_in_increases_quantity_and_logs_transaction(self):
        self.client.post(self.url, {"transaction_type": "IN", "quantity": 5, "note": ""})
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 15)
        self.assertEqual(StockTransaction.objects.count(), 1)

    def test_stock_out_decreases_quantity(self):
        self.client.post(self.url, {"transaction_type": "OUT", "quantity": 4, "note": ""})
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 6)

    def test_cannot_remove_more_than_available(self):
        self.client.post(self.url, {"transaction_type": "OUT", "quantity": 100, "note": ""})
        self.product.refresh_from_db()
        # Quantity should be unchanged and no transaction recorded.
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(StockTransaction.objects.count(), 0)


class ProductListViewTests(TestCase):
    def setUp(self):
        Product.objects.create(name="Wireless Mouse", sku="ELEC-001", quantity=5)
        Product.objects.create(name="Office Chair", sku="FURN-001", quantity=2)

    def test_list_page_loads(self):
        response = self.client.get(reverse("product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")

    def test_search_filters_results(self):
        response = self.client.get(reverse("product_list"), {"q": "chair"})
        self.assertContains(response, "Office Chair")
        self.assertNotContains(response, "Wireless Mouse")
