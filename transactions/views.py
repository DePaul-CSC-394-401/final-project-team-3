from django.shortcuts import render, redirect
from .models import Transaction
from .forms import PurchaseForm, WithdrawForm, DepositForm
from .models import BankAccount
from decimal import Decimal


def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'purchase'

            bank_account = transaction.bank_account
            if bank_account.account_type == 'credit':
                # credit card, increase the balance
                bank_account.account_balance += Decimal(transaction.amount)
            else:
                # non-credit accounts, decrease the balance
                bank_account.account_balance -= Decimal(transaction.amount)
            bank_account.save()

            transaction.save()
            return redirect('transaction_list')
    return redirect('transaction_list') 

def add_withdraw(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'withdraw'

            if not transaction.category:
                transaction.category = 'transfer'

            bank_account = transaction.bank_account
            bank_account.account_balance -= Decimal(transaction.amount)
            bank_account.save()

            transaction.save()
            return redirect('transaction_list')
    return redirect('transaction_list') 

def add_deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'deposit'

            if not transaction.category:
                # credit card account, default to 'credit'
                if transaction.bank_account.account_type == 'credit':
                    transaction.category = 'credit'
                else:
                    transaction.category = 'income'

            bank_account = transaction.bank_account
            if bank_account.account_type == 'credit':
                # decrease the balance for credit cards
                bank_account.account_balance -= Decimal(transaction.amount)
            else:
                # increase the balance for non-credit accounts
                bank_account.account_balance += Decimal(transaction.amount)
            bank_account.save()

            transaction.save()
            return redirect('transaction_list')
    return redirect('transaction_list')


def transaction_list(request):
    # get user's bank accounts
    accounts = BankAccount.objects.filter(user=request.user)

    # fetch all transactions for the user's accounts by default
    transactions = Transaction.objects.filter(bank_account__in=accounts)

    # get the sort_by query parameter
    sort_by = request.GET.get('sort_by', 'date')

    # filter by selected account
    selected_account = request.GET.get('account')
    if sort_by == 'account' and selected_account:
        transactions = transactions.filter(bank_account__id=selected_account)

    # filter by selected date
    selected_date = request.GET.get('date')
    if sort_by == 'date' and selected_date:
        transactions = transactions.filter(date=selected_date)

    # filter by category
    selected_category = request.GET.get('category')
    if selected_category:
        transactions = transactions.filter(category=selected_category)

    # default sorting
    transactions = transactions.order_by('-date')

    # forns
    deposit_form = DepositForm(user=request.user)
    withdraw_form = WithdrawForm(user=request.user)
    purchase_form = PurchaseForm(user=request.user)

    # unique categories
    categories = Transaction.TRANSACTION_CATEGORIES

    return render(request, 'transaction_list.html', {
        'transactions': transactions,
        'accounts': accounts,
        'sort_by': sort_by,
        'deposit_form': deposit_form,
        'withdraw_form': withdraw_form,
        'purchase_form': purchase_form,
        'categories': categories,
        'selected_category': selected_category,
    })