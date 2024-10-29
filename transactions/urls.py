
from django.urls import path
from . import views

urlpatterns = [
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add_purchase/', views.add_purchase, name='add_purchase'),
    path('transactions/add_withdraw/', views.add_withdraw, name='add_withdraw'),
    path('transactions/add_deposit/', views.add_deposit, name='add_deposit'),
]
