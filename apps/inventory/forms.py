from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'purchase_price', 'initial_stock', 'remaining_stock']
    