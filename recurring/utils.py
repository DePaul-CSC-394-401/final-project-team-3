# recurring/utils.py
from datetime import timedelta
from django.utils import timezone
from .models import RecurringTransaction
from transactions.models import Transaction
from bank.models import BankAccount
import logging
from recurring.models import RecurringTransaction



def generate_recurring_transactions(user):
    now = timezone.now()
    print(f"Generating recurring transactions at {now}")

    # Fetch the user's bank accounts
    user_accounts = BankAccount.objects.filter(user=user)
    print(f"User accounts: {user_accounts}")

    # Fetch all recurring transactions for the user's bank accounts
    all_recurring_transactions = RecurringTransaction.objects.filter(bank_account__in=user_accounts)
    print("Filtered Recurring Transactions:")
    for recurring_transaction in all_recurring_transactions:
        print(recurring_transaction)

        if recurring_transaction.frequency == 'one_minute':
            # Fetch the last transaction time for this bank account and recurring transaction name
            last_transaction = Transaction.objects.filter(
                bank_account=recurring_transaction.bank_account,
                name=recurring_transaction.name  # Filter by the name of the recurring transaction
            ).order_by('-date').first()
            # Print the last transaction for debugging
            print(f"Last transaction for {recurring_transaction.name}: {last_transaction}")

            last_transaction_time = last_transaction.date if last_transaction else None
            # Print the last transaction time for debugging
            print(f"Last transaction time: {last_transaction_time}")

            # Calculate the number of new transactions to create
            if last_transaction_time:
                time_diff = now - last_transaction_time
                # Calculate how many minutes have passed
                minutes_passed = time_diff.total_seconds() // 60
            else:
                minutes_passed = 1  # If there's no last transaction, we can create at least one new transaction

            # Create new transactions for each minute passed
            for _ in range(int(minutes_passed)):
                new_transaction = Transaction.objects.create(
                    bank_account=recurring_transaction.bank_account,
                    amount=recurring_transaction.amount,
                    transaction_type=recurring_transaction.transaction_type,
                    date=now,
                    category=recurring_transaction.category,
                    name=recurring_transaction.name,  # Use the name from the recurring transaction
                )

                 # Update the bank account balance
                bank_account = recurring_transaction.bank_account
                if bank_account.account_type == 'credit':
                    bank_account.account_balance += new_transaction.amount
                elif bank_account.account_type in ['checking', 'savings']:
                    bank_account.account_balance -= new_transaction.amount
                bank_account.save()

                new_transaction.save()
                print(f"Created transaction: {new_transaction}")

        elif recurring_transaction.frequency == 'monthly':
            last_transaction = Transaction.objects.filter(
                bank_account=recurring_transaction.bank_account,
                name=recurring_transaction.name
            ).order_by('-date').first()
            
            last_transaction_time = last_transaction.date if last_transaction else None
            print(f"Last monthly transaction time: {last_transaction_time}")

            # Calculate total seconds in a month (30 days)
            seconds_in_a_month = 30 * 24 * 60 * 60

            if last_transaction_time is None or (now - last_transaction_time).total_seconds() >= seconds_in_a_month:
                new_transaction = Transaction.objects.create(
                    bank_account=recurring_transaction.bank_account,
                    amount=recurring_transaction.amount,
                    transaction_type=recurring_transaction.transaction_type,
                    date=now,
                    category=recurring_transaction.category,
                    name=recurring_transaction.name,
                )

                 # Update the bank account balance
                bank_account = recurring_transaction.bank_account
                if bank_account.account_type == 'credit':
                    bank_account.account_balance += new_transaction.amount
                elif bank_account.account_type in ['checking', 'savings']:
                    bank_account.account_balance -= new_transaction.amount
                bank_account.save()

                new_transaction.save()

                print(f"Created monthly transaction: {new_transaction}")
            

    return