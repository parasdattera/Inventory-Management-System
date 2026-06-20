from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, F
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductCreateForm, ProductForm, StockAdjustForm
from .models import Category, Product, StockTransaction


def dashboard(request):
    """Landing page with a few headline numbers and the low-stock list."""
    products = Product.objects.all()
    low_stock = products.filter(quantity__lte=F("reorder_level"))

    context = {
        "total_products": products.count(),
        "total_units": products.aggregate(total=Sum("quantity"))["total"] or 0,
        "low_stock_count": low_stock.count(),
        "low_stock_products": low_stock[:10],
        "recent_transactions": StockTransaction.objects.select_related("product")[:10],
    }
    return render(request, "inventory/dashboard.html", context)


def product_list(request):
    """List of all products with a search box and category filter."""
    products = Product.objects.select_related("category")

    search = request.GET.get("q", "").strip()
    if search:
        products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))

    category_id = request.GET.get("category", "")
    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "search": search,
        "selected_category": category_id,
    }
    return render(request, "inventory/product_list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        "product": product,
        "transactions": product.transactions.all()[:20],
        "form": StockAdjustForm(),
    }
    return render(request, "inventory/product_detail.html", context)


def product_create(request):
    if request.method == "POST":
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' created.")
            return redirect(product)
    else:
        form = ProductCreateForm()
    return render(request, "inventory/product_form.html", {"form": form, "title": "Add Product"})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated.")
            return redirect(product)
    else:
        form = ProductForm(instance=product)
    return render(request, "inventory/product_form.html", {"form": form, "title": "Edit Product"})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, f"Product '{product.name}' deleted.")
        return redirect("product_list")
    return render(request, "inventory/product_confirm_delete.html", {"product": product})


def stock_adjust(request, pk):
    """Add or remove stock for a product and log it as a transaction."""
    product = get_object_or_404(Product, pk=pk)

    if request.method != "POST":
        return redirect(product)

    form = StockAdjustForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please enter a valid quantity.")
        return redirect(product)

    movement = form.save(commit=False)
    movement.product = product

    if movement.transaction_type == StockTransaction.STOCK_OUT and movement.quantity > product.quantity:
        messages.error(
            request,
            f"Cannot remove {movement.quantity} units - only {product.quantity} in stock.",
        )
        return redirect(product)

    # Update the product quantity and save the transaction together, so we
    # never end up with one without the other.
    with transaction.atomic():
        if movement.transaction_type == StockTransaction.STOCK_IN:
            product.quantity += movement.quantity
        else:
            product.quantity -= movement.quantity
        product.save(update_fields=["quantity", "updated_at"])
        movement.save()

    messages.success(request, "Stock updated.")
    return redirect(product)
