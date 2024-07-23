from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('report/products/', views.product_report, name='product_report'),
    path('report/products/clear/', views.clear_report, name='clear_report'),
    path('save_report/', views.save_report, name='save_report'),
    path('report/history/', views.report_history, name='report_history'),
    path('add_sale/', views.add_sale, name='add_sale'),
    path('add_product/', views.add_product, name='add_product'),


]   