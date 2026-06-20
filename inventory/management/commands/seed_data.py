from django.core.management.base import BaseCommand

from inventory.models import Category, Product, StockTransaction


class Command(BaseCommand):
    help = "Populate the database with some sample categories, products and stock movements."

    def handle(self, *args, **options):
        # Start clean so the command can be run repeatedly without piling up data.
        StockTransaction.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        categories = {}
        for name in ["Electronics", "Stationery", "Groceries", "Furniture"]:
            categories[name] = Category.objects.create(name=name)

        products = [
            ("Wireless Mouse", "ELEC-001", "Electronics", 799, 25, 10),
            ("USB-C Cable", "ELEC-002", "Electronics", 299, 8, 15),
            ("Mechanical Keyboard", "ELEC-003", "Electronics", 3499, 12, 5),
            ("A4 Notebook", "STAT-001", "Stationery", 60, 200, 50),
            ("Ballpoint Pen (Pack of 10)", "STAT-002", "Stationery", 120, 4, 20),
            ("Green Tea (100 bags)", "GROC-001", "Groceries", 450, 30, 10),
            ("Office Chair", "FURN-001", "Furniture", 5999, 2, 3),
        ]

        for name, sku, category, price, quantity, reorder in products:
            product = Product.objects.create(
                name=name,
                sku=sku,
                category=categories[category],
                price=price,
                quantity=quantity,
                reorder_level=reorder,
            )
            # Record the opening stock as a "stock in" transaction.
            StockTransaction.objects.create(
                product=product,
                transaction_type=StockTransaction.STOCK_IN,
                quantity=quantity,
                note="Opening stock",
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Category.objects.count()} categories and {Product.objects.count()} products."
        ))
