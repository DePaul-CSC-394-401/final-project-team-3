from django.shortcuts import render, redirect
from .models import BankAccount
from .forms import BankAccountForm


# Create your views here.
def dashboard(request):
    accounts = BankAccount.objects.all()
    return render(request, 'dashboard.html', {'accounts': accounts})

def deposit(self, amount):
        self.account_balance += amount
        self.save()

def withdraw(self, amount):
    if self.account_balance >= amount:
        self.account_balance -= amount
        self.save() 

def create_account(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BankAccountForm()
    return render(request, 'create_account.html', {'form': form})