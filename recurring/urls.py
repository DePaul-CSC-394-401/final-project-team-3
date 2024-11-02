from django.urls import path
from . import views

urlpatterns = [
    path('', views.recurring_transaction_list, name='recurring_transaction_list'),
    path('add/', views.add_recurring_transaction, name='add_recurring_transaction'),
    path('edit/<int:pk>/', views.edit_recurring_transaction, name='edit_recurring_transaction'),
    path('delete/<int:pk>/', views.delete_recurring_transaction, name='delete_recurring_transaction'),
]