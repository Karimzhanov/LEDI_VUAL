from django.db import models
from datetime import timedelta
import datetime
from django.utils import timezone

# Create your models here.
class Product(models.Model):
    name = models.CharField("Название", max_length=100)
    category = models.CharField("Категория", max_length=100)
    purchase_price = models.DecimalField("Цена покупки", max_digits=7, decimal_places=2)
    initial_stock = models.PositiveIntegerField("Начальный запас")
    remaining_stock = models.PositiveIntegerField("Остаток на складе")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество")
    sale_price = models.DecimalField("Цена продажи", max_digits=7, decimal_places=2, default=0.0)
    sale_date = models.DateField("Дата продажи", default=datetime.date.today)

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'

class Report(models.Model):
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    report_data = models.TextField("Данные отчета")  # храним отчет в виде текстового поля

    def __str__(self):
        return f'Отчет от {self.created_at}'


    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"
