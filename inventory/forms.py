from django import forms

from .models import Product, StockTransaction


class ProductForm(forms.ModelForm):
    """Used for both creating and editing a product.

    Note: `quantity` is intentionally left out here. Once a product exists,
    stock should only change through a StockTransaction (stock in / stock out)
    so we always keep a proper history. The starting quantity is set when the
    product is first created (see ProductCreateForm below).
    """

    class Meta:
        model = Product
        fields = ["name", "sku", "category", "description", "price", "reorder_level"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the bootstrap class to every field so the form looks consistent.
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ProductCreateForm(ProductForm):
    """Same as ProductForm but lets you set an opening quantity on creation."""

    class Meta(ProductForm.Meta):
        fields = ProductForm.Meta.fields + ["quantity"]


class StockAdjustForm(forms.ModelForm):
    """Records a stock-in or stock-out movement for a product."""

    class Meta:
        model = StockTransaction
        fields = ["transaction_type", "quantity", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
