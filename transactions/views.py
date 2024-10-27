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
            # Category is handled by the form, no need for default

            # Adjust the balance for the purchase
            bank_account = transaction.bank_account
            if bank_account.account_type == 'credit':
                # If it's a credit card, increase the balance
                bank_account.account_balance += Decimal(transaction.amount)
            else:
                # For non-credit accounts, decrease the balance
                bank_account.account_balance -= Decimal(transaction.amount)
            bank_account.save()

            transaction.save()
            return redirect('transaction_list')
    return redirect('transaction_list')  # Redirect if not POST or form invalid


def add_withdraw(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'withdraw'

            # Set default category to 'transfer' if none selected
            if not transaction.category:
                transaction.category = 'transfer'

            # Adjust the balance for the withdrawal
            bank_account = transaction.bank_account
            bank_account.account_balance -= Decimal(transaction.amount)
            bank_account.save()

            transaction.save()
            return redirect('transaction_list')
    return redirect('transaction_list')  # Redirect if not POST or form invalid


def add_deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'deposit'

            # Set default category based on the transaction
            if not transaction.category:
                # If it's a credit card account, default to 'credit'
                if transaction.bank_account.account_type == 'credit':
                    transaction.category = 'credit'
                else:
                    transaction.category = 'income'

            # Adjust the balance for the deposit
            bank_account = transaction.bank_account
            if bank_account.account_type == 'credit':
                # Decrease the balance for credit cards
                bank_account.account_balance -= Decimal(transaction.amount)
            else:
                # Increase the balance for non-credit accounts
                bank_account.account_balance += Decimal(transaction.amount)
            bank_account.save()

            transaction.save()
            return redirect('transaction_list')
    return redirect('transaction_list')  # Redirect if not POST or form invalid


def transaction_list(request):
    # Get the user's bank accounts
    accounts = BankAccount.objects.filter(user=request.user)

    # Fetch all transactions for the user's accounts by default
    transactions = Transaction.objects.filter(bank_account__in=accounts)

    # Get the sort_by query parameter (default is by date)
    sort_by = request.GET.get('sort_by', 'date')

    # Filter by selected account if 'account' is chosen
    selected_account = request.GET.get('account')
    if sort_by == 'account' and selected_account:
        transactions = transactions.filter(bank_account__id=selected_account)

    # Filter by selected date if 'date' is chosen
    selected_date = request.GET.get('date')
    if sort_by == 'date' and selected_date:
        transactions = transactions.filter(date=selected_date)

    # Filter by category if specified
    selected_category = request.GET.get('category')
    if selected_category:
        transactions = transactions.filter(category=selected_category)

    # Apply default sorting (by date)
    transactions = transactions.order_by('-date')

    # Initialize forms for each transaction type
    deposit_form = DepositForm(user=request.user)
    withdraw_form = WithdrawForm(user=request.user)
    purchase_form = PurchaseForm(user=request.user)

    # Get unique categories for the filter dropdown
    categories = Transaction.TRANSACTION_CATEGORIES

    return render(request, 'transaction_list.html', {
        'transactions': transactions,
        'accounts': accounts,
        'sort_by': sort_by,
        'deposit_form': deposit_form,
        'withdraw_form': withdraw_form,
        'purchase_form': purchase_form,
        'categories': categories,  # Add categories for filtering
        'selected_category': selected_category,  # Currently selected category
    })