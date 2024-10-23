"""
URL configuration for finalProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from bank import views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),

    # Bank-related URLs
    path('create/', views.create_account, name='create_account'),
    path('account/<str:account_no>/', views.view_account, name='view_account'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Home/dashboard view
    
    path('edit/<int:account_id>/', views.edit_account, name='edit_account'), 
    path('delete/<int:account_id>/', views.delete_account, name='delete_account'), 
     
    # Include the URLs from the transactions app
    path('', include('transactions.urls')),  # This will include the URLs from the transactions app

    # UserAuth-related URLs
    path('auth/', include('UserAuth.urls')),  # Add this to include the UserAuth URLs
]
