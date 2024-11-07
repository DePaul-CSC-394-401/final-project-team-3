from django.shortcuts import render, redirect, get_object_or_404
from .models import BankAccount
from .forms import BankAccountForm
from transactions.models import Transaction  # Import the Transaction model
from transactions.forms import DepositForm, WithdrawForm, PurchaseForm  # Import the forms
from recurring.utils import generate_recurring_transactions
from recurring.models import RecurringTransaction
from django.db.models import Sum
import json
# Create your views here.

def dashboard(request):
    # get the users bank accounts
    #generate_recurring_transactions(request.user)
    accounts = BankAccount.objects.filter(user=request.user)

    generate_recurring_transactions(request.user) #recurring transactions

    # fetch the 5 most recent transactions for all accounts
    recent_transactions = Transaction.objects.filter(bank_account__in=accounts).order_by('-date')[:5]

    # forms
    deposit_form = DepositForm(user=request.user)
    withdraw_form = WithdrawForm(user=request.user)
    purchase_form = PurchaseForm(user=request.user)

    return render(request, 'dashboard.html', {
        'accounts': accounts,
        'recent_transactions': recent_transactions,
        'deposit_form': deposit_form,
        'withdraw_form': withdraw_form,
        'purchase_form': purchase_form,
    })

def create_account(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            #form.save()
            bank_account = form.save(commit=False)  # do not save yet
            bank_account.user = request.user
            bank_account.save()
            return redirect('dashboard')
    else:
        form = BankAccountForm()
    return render(request, 'create_account.html', {'form': form})




def view_account(request, account_no):
    # get the specific account for the user
    account = get_object_or_404(BankAccount, account_no=account_no, user=request.user)

    # fetch the transactions for this account
    transactions = Transaction.objects.filter(bank_account=account).order_by('-date')

    # Calculate category totals for this account
    category_totals = (Transaction.objects
                       .filter(bank_account=account)
                       .values('category')
                       .annotate(total=Sum('amount'))
                       .order_by('-total'))

    # Convert Decimal to float for JSON serialization
    category_totals_json = json.dumps([{
        'category': item['category'],
        'total': float(item['total'])
    } for item in category_totals])

    return render(request, 'view_account.html', {
        'account': account,
        'transactions': transactions,
        'category_totals_json': category_totals_json,
        'categories': Transaction.TRANSACTION_CATEGORIES,
    })
    


def edit_account(request, account_id):
    account = get_object_or_404(BankAccount, pk=account_id, user=request.user)
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BankAccountForm(instance=account)
    return render(request, 'edit_account.html', {'form': form, 'account': account})


def delete_account(request, account_id):
   account = get_object_or_404(BankAccount, pk=account_id, user=request.user)
   #account = get_object_or_404(BankAccount, pk=account_id)
   if request.method == 'POST':
       account.delete()
       return redirect('dashboard')
   return render(request, 'delete_account.html', {'account': account})
  
