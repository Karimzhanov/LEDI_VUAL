from django.shortcuts import render, redirect
from .models import Report, Product, Sale
from django.utils import timezone
import json,datetime
from django.db.models import Sum, F
from django.conf.urls import handler404
from django.urls import reverse
from .forms import ProductForm  # предполагается, что у вас есть форма для продукта



def index(request):
    return render(request, 'index.html')


def product_report(request):
    report = Sale.objects.values('product__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price')),
        som=Sum(F('quantity') * F('price'))  # Пример расчета СОМ, адаптируйте под ваши нужды
    )

    total_revenue = report.aggregate(total=Sum('total_revenue'))['total'] or 0
    total_som = report.aggregate(total=Sum('som'))['total'] or 0

    remaining_products = Product.objects.annotate(
        calculated_remaining_stock=F('initial_stock') - Sum('sale__quantity')
    )

    context = {
        'report': report,
        'total_revenue': total_revenue,
        'total_som': total_som,
        'remaining_products': remaining_products,
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
            total_revenue=Sum(F('quantity') * F('product__price'))
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

def report_history(request):
    reports = Report.objects.all().order_by('-created_at')
    decoded_reports = []

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

    return render(request, 'report_history.html', {'reports': decoded_reports})



def add_sale(request):
    if request.method == 'POST':
        product_id = request.POST['product']
        quantity = int(request.POST['quantity'])
        sale_date = request.POST.get('sale_date', timezone.now().date())  # Или ваша логика получения даты

        product = Product.objects.get(id=product_id)
        price = product.price * quantity  # Если цена за штуку в продукте

        sale = Sale(product=product, quantity=quantity, price=price, sale_date=sale_date)
        sale.save()

        return redirect('index')

    products = Product.objects.all()
    return render(request, 'add_sale.html', {'products': products})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # перенаправление на главную страницу после успешного добавления
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