from django.urls import path
from . import views

urlpatterns = [
    # URL for the list of transactions
    path('transactions/', views.transaction_list, name='transaction_list'),

    # URL for adding a new transaction
    path('transactions/add/', views.add_transaction, name='add_transaction'),
]
