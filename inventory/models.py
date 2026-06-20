from django.db import models
from django.urls import reverse


class Category(models.Model):
    """A simple grouping for products (e.g. Electronics, Stationery)."""

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """An item we keep stock of."""

    name = models.CharField(max_length=200)
    sku = models.CharField("SKU", max_length=50, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    # When quantity drops to/below this number we flag the product as low on stock.
    reorder_level = models.PositiveIntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.pk])

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level


class StockTransaction(models.Model):
    """A record of stock coming in or going out for a product.

    Keeping a history means the current quantity is always explainable -
    you can see every change instead of just the final number.
    """

    STOCK_IN = "IN"
    STOCK_OUT = "OUT"
    TYPE_CHOICES = [
        (STOCK_IN, "Stock In"),
        (STOCK_OUT, "Stock Out"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    transaction_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.name} x{self.quantity}"
