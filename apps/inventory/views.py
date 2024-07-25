from django.shortcuts import render, redirect
from .models import Report, Product, Sale
from django.utils import timezone
import json
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.conf.urls import handler404
from django.urls import reverse
from datetime import datetime, timedelta

from .forms import ProductForm  # предполагается, что у вас есть форма для продукта



def index(request):
    return render(request, 'index.html')


def product_report(request):
    report = Sale.objects.values('product__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('sale_price')),
        total_purchase=Sum(F('quantity') * F('product__purchase_price')),
        remaining_stock=Sum('product__initial_stock') - Sum('quantity'),
    ).annotate(
        profit=ExpressionWrapper(F('total_revenue') - F('total_purchase'), output_field=DecimalField())
    )

    total_revenue = report.aggregate(total=Sum('total_revenue'))['total'] or 0
    total_purchase = report.aggregate(total=Sum('total_purchase'))['total'] or 0
    total_profit = report.aggregate(total=Sum('profit'))['total'] or 0

    context = {
        'report': report,
        'total_revenue': total_revenue,
        'total_purchase': total_purchase,
        'total_profit': total_profit,
    }
    return render(request, 'product_report.html', context)


def report_view(request):
    reports = Report.objects.all()
    report_data = Sale.objects.values('product__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
    )
    total_revenue = report_data.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
    
    context = {
        'report': report_data,
        'total_revenue': total_revenue,
        'reports': reports,
    }
    return render(request, 'report.html', context)





def save_report(request):
    if request.method == 'POST':
        report_data = Sale.objects.values('product__name').annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('sale_price'))
        )
        total_revenue = report_data.aggregate(total_revenue=Sum('total_revenue'))['total_revenue'] or 0

        # Подготовка данных для сохранения в формате JSON
        report_content = [
            {
                'product__name': item['product__name'],
                'total_sold': item['total_sold'],
                'total_revenue': float(item['total_revenue']) if item['total_revenue'] is not None else 0.0
            } for item in report_data
        ]

        report = Report(report_data=json.dumps(report_content))
        report.save()
        return redirect('report_history')
    
        
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, F
from decimal import Decimal
import json
from django.shortcuts import render
from .models import Report, Sale

def report_history(request):
    # Получение всех отчетов
    reports = Report.objects.all().order_by('-created_at')
    decoded_reports = []

    # Декодирование данных отчетов
    for report in reports:
        try:
            decoded_data = json.loads(report.report_data)
            decoded_reports.append({
                'created_at': report.created_at,
                'report_data': decoded_data
            })
        except json.JSONDecodeError:
            decoded_reports.append({
                'created_at': report.created_at,
                'report_data': []
            })

    # Определение начала текущего периода
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())
    start_of_month = now.replace(day=1)
    start_of_year = now.replace(month=1, day=1)

    # Получение данных о продажах за каждый период
    weekly_sales = Sale.objects.filter(sale_date__gte=start_of_week, sale_date__lte=now)
    monthly_sales = Sale.objects.filter(sale_date__gte=start_of_month, sale_date__lte=now)
    yearly_sales = Sale.objects.filter(sale_date__gte=start_of_year, sale_date__lte=now)

    # Рассчет статистики
    def calculate_stats(sales):
        return {
            'sold_products': sales.aggregate(total=Sum('quantity'))['total'] or 0,
            'revenue': sales.aggregate(total=Sum(F('quantity') * F('sale_price')))['total'] or Decimal('0.0')
        }

    # Подсчет текущей статистики
    weekly_stats = calculate_stats(weekly_sales)
    monthly_stats = calculate_stats(monthly_sales)
    yearly_stats = calculate_stats(yearly_sales)

    # Подсчет исторической статистики из отчетов
    historical_weekly_stats = {'sold_products': 0, 'revenue': Decimal('0.0')}
    historical_monthly_stats = {'sold_products': 0, 'revenue': Decimal('0.0')}
    historical_yearly_stats = {'sold_products': 0, 'revenue': Decimal('0.0')}

    for report in decoded_reports:
        report_date = report['created_at']
        report_data = report['report_data']

        if report_date >= start_of_week:
            historical_weekly_stats['sold_products'] += sum(item['total_sold'] for item in report_data)
            historical_weekly_stats['revenue'] += sum(Decimal(item['total_revenue']) for item in report_data)
        
        if report_date >= start_of_month:
            historical_monthly_stats['sold_products'] += sum(item['total_sold'] for item in report_data)
            historical_monthly_stats['revenue'] += sum(Decimal(item['total_revenue']) for item in report_data)
        
        if report_date >= start_of_year:
            historical_yearly_stats['sold_products'] += sum(item['total_sold'] for item in report_data)
            historical_yearly_stats['revenue'] += sum(Decimal(item['total_revenue']) for item in report_data)

    # Объединение текущей и исторической статистики
    weekly_stats['sold_products'] += historical_weekly_stats['sold_products']
    weekly_stats['revenue'] += historical_weekly_stats['revenue']
    
    monthly_stats['sold_products'] += historical_monthly_stats['sold_products']
    monthly_stats['revenue'] += historical_monthly_stats['revenue']
    
    yearly_stats['sold_products'] += historical_yearly_stats['sold_products']
    yearly_stats['revenue'] += historical_yearly_stats['revenue']

    # Подготовка контекста для шаблона
    context = {
        'reports': decoded_reports,
        'weekly_stats': weekly_stats,
        'monthly_stats': monthly_stats,
        'yearly_stats': yearly_stats,
    }

    return render(request, 'report_history.html', context)



from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from apps.inventory.models import Product, Sale

def add_sale(request):
    if request.method == 'POST':
        try:
            product_id = request.POST['product']
            quantity = request.POST['quantity']
            sale_price = request.POST['sale_price']
            sale_date = request.POST.get('sale_date', timezone.now().date())  # Или ваша логика получения даты

            # Проверка количества
            try:
                quantity = int(quantity)
            except ValueError:
                messages.error(request, "Некорректное значение количества.")
                return render(request, 'add_sale.html', {'products': Product.objects.all()})

            # Проверка цены
            try:
                sale_price = Decimal(sale_price)
            except InvalidOperation:
                messages.error(request, "Некорректное значение цены.")
                return render(request, 'add_sale.html', {'products': Product.objects.all()})

            # Проверка существования продукта
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                messages.error(request, "Выбранный продукт не существует.")
                return render(request, 'add_sale.html', {'products': Product.objects.all()})

            sale = Sale(product=product, quantity=quantity, sale_price=sale_price, sale_date=sale_date)

            try:
                sale.save()
            except Exception as e:
                messages.error(request, f"Ошибка при сохранении продажи: {e}")
                return render(request, 'add_sale.html', {'products': Product.objects.all()})

            return redirect('index')

        except Exception as e:
            messages.error(request, f"Неожиданная ошибка: {e}")
            return render(request, 'add_sale.html', {'products': Product.objects.all()})

    products = Product.objects.all()
    return render(request, 'add_sale.html', {'products': products})



def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def clear_report(request):
    if request.method == 'POST':
        # Логика для сброса данных отчёта
        Sale.objects.all().delete()  # Удалить все записи о продажах
        return JsonResponse({'status': 'success'})
    
def custom_404(request, exception):
    return render(request, '404.html', status=404)

handler404 = custom_404