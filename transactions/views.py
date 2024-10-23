from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
from .models import BankAccount


def transaction_list(request):
    #transactions = Transaction.objects.all()
    accounts = BankAccount.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(bank_account__in=accounts)
    #transactions = Transaction.objects.filter(user=request.user) 
    return render(request, 'transaction_list.html', {'transactions': transactions})


# Add Transaction View (for adding new transactions)
def add_transaction(request):
    if request.method == 'POST':
        #form = TransactionForm(request.POST)
        form = TransactionForm(user=request.user, data=request.POST)  # Pass the user here
        if form.is_valid():
            transaction = form.save(commit=False)  # Don't save to DB yet, we need to modify the account balance

            #ADDED THIS LINE
            #transaction.user = request.user

            # Get the associated bank account
            bank_account = transaction.bank_account

            # Update the balance based on the account type and transaction type
            if bank_account.account_type == 'credit':
                print(f"Credit card detected: {bank_account.account_name}")  # Debug print
                print(f"Transaction amount: {type(transaction.amount)}")  # Debugging print
                bank_account.account_balance = bank_account.account_balance + transaction.amount
            else:
                print(f"Non-credit account detected: {bank_account.account_name}")  # Debug print
                print(f"Transaction amount: {transaction.amount}")  # Debugging print

                bank_account.account_balance = bank_account.account_balance - transaction.amount

            # Save the updated balance to the database
            bank_account.save()

            # Now save the transaction itself
            transaction.save()

            return redirect('transaction_list')
    else:
        #form = TransactionForm()
        form = TransactionForm(user=request.user)  # Pass the user here

    return render(request, 'add_transaction.html', {'form': form})
