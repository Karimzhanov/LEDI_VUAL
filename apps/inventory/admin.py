from django.contrib import admin
from .models import Product, Sale, Report

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'purchase_price', 'remaining_stock')
admin.site.register(Sale)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'report_data')