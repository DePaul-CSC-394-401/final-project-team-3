from django.shortcuts import render, redirect, get_object_or_404
from .models import BankAccount
from .forms import BankAccountForm


# Create your views here.
def dashboard(request):
    accounts = BankAccount.objects.all()
    return render(request, 'dashboard.html', {'accounts': accounts})

def create_account(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BankAccountForm()
    return render(request, 'create_account.html', {'form': form})

def view_account(request, account_no):
    account = get_object_or_404(BankAccount, account_no=account_no)
    return render(request, 'view_account.html', {'account': account})