
from django.shortcuts import render

# Create your views here.

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
    else:
        form = PurchaseForm(user=request.user)

    return render(request, 'add_purchase.html', {'form': form})


def add_withdraw(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'withdraw'

            # Adjust the balance for the withdrawal
            bank_account = transaction.bank_account
            bank_account.account_balance -= Decimal(transaction.amount)
            bank_account.save()

            transaction.save()
            return redirect('transaction_list')
    else:
        form = WithdrawForm(user=request.user)

    return render(request, 'add_withdraw.html', {'form': form})


def add_deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'deposit'

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
    else:
        form = DepositForm(user=request.user)

    return render(request, 'add_deposit.html', {'form': form})

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

    # Apply default sorting (by date)
    transactions = transactions.order_by('-date')

    # Initialize forms for each transaction type
    deposit_form = DepositForm(user=request.user)
    withdraw_form = WithdrawForm(user=request.user)
    purchase_form = PurchaseForm(user=request.user)

    return render(request, 'transaction_list.html', {
        'transactions': transactions,
        'accounts': accounts,
        'sort_by': sort_by,
        'deposit_form': deposit_form,
        'withdraw_form': withdraw_form,
        'purchase_form': purchase_form,
    })


# Add Transaction View (for adding new transactions)
# def add_transaction(request):
#     if request.method == 'POST':
#         #form = TransactionForm(request.POST)
#         form = TransactionForm(user=request.user, data=request.POST)  # Pass the user here
#         if form.is_valid():
#             transaction = form.save(commit=False)  # Don't save to DB yet, we need to modify the account balance
#
#             #ADDED THIS LINE
#             #transaction.user = request.user
#
#             # Get the associated bank account
#             bank_account = transaction.bank_account
#
#             # Update the balance based on the account type and transaction type
#             if bank_account.account_type == 'credit':
#                 print(f"Credit card detected: {bank_account.account_name}")  # Debug print
#                 print(f"Transaction amount: {type(transaction.amount)}")  # Debugging print
#                 bank_account.account_balance = bank_account.account_balance + transaction.amount
#             else:
#                 print(f"Non-credit account detected: {bank_account.account_name}")  # Debug print
#                 print(f"Transaction amount: {transaction.amount}")  # Debugging print
#
#                 bank_account.account_balance = bank_account.account_balance - transaction.amount
#
#             # Save the updated balance to the database
#             bank_account.save()
#
#             # Now save the transaction itself
#             transaction.save()
#
#             return redirect('transaction_list')
#     else:
#         #form = TransactionForm()
#         form = TransactionForm(user=request.user)  # Pass the user here
#
#     return render(request, 'add_transaction.html', {'form': form})
