
from django.urls import path
from . import views

urlpatterns = [
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add_purchase/', views.add_purchase, name='add_purchase'),  # URL for adding a Purchase
    path('transactions/add_withdraw/', views.add_withdraw, name='add_withdraw'),  # URL for adding a Withdraw
    path('transactions/add_deposit/', views.add_deposit, name='add_deposit'),  # URL for adding a Deposit
]
