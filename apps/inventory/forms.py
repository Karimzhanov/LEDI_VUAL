from django import forms
from .models import Product  # предположим, что у вас есть модель Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'initial_stock', 'remaining_stock']
