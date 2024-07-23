from django.db import models
from datetime import timedelta
import datetime
from django.utils import timezone

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    initial_stock = models.PositiveIntegerField()
    remaining_stock = models.PositiveIntegerField()



    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    sale_date = models.DateField(default=datetime.date.today)

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'



class Report(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    report_data = models.TextField()  # храним отчет в виде текстового поля

    def __str__(self):
        return f'Report from {self.created_at}'


    @classmethod
    def delete_old_reports(cls):
        cutoff_date = timezone.now() - timedelta(days=30)
        cls.objects.filter(created_at__lt=cutoff_date).delete()

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"


