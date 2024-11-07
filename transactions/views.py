from django.shortcuts import render, redirect
from .models import Transaction
from .forms import PurchaseForm, WithdrawForm, DepositForm
from .models import BankAccount
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json
from django.db.models import Min, Max
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # You might need to install python-dateutil




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

    # forms
    deposit_form = DepositForm(user=request.user)
    withdraw_form = WithdrawForm(user=request.user)
    purchase_form = PurchaseForm(user=request.user)

    ## Start of visualizations
    # unique categories
    categories = Transaction.TRANSACTION_CATEGORIES

    category_totals = list(Transaction.objects
                           .filter(bank_account__in=accounts)
                           .values('category')
                           .annotate(total=Sum('amount'))
                           .order_by('-total'))

    # Convert Decimal to float for JSON serialization
    for item in category_totals:
        item['total'] = float(item['total'])

    # Monthly totals
    monthly_totals = list(Transaction.objects
                          .filter(bank_account__in=accounts)
                          .annotate(month=TruncMonth('date'))
                          .values('month')
                          .annotate(total=Sum('amount'))
                          .order_by('month'))

    monthly_totals_json = json.dumps([{
        'month': item['month'].strftime('%Y-%m-%d'),  # Format date as string
        'total': float(item['total'])
    } for item in monthly_totals])

    # Convert Decimal to float
    for item in monthly_totals:
        item['total'] = float(item['total'])


        # Convert data to JSON for JavaScript
    category_totals_json = json.dumps(category_totals)

    # Get category names dictionary
    category_names = dict(Transaction.TRANSACTION_CATEGORIES)
    date_range = Transaction.objects.filter(bank_account__in=accounts).aggregate(
        min_date=Min('date'),
        max_date=Max('date')
    )

    if date_range['min_date'] and date_range['max_date']:
        # Create a list of all months between min and max date
        current_date = date_range['min_date'].replace(day=1)
        end_date = date_range['max_date'].replace(day=1)
        all_months = []

        while current_date <= end_date:
            all_months.append(current_date)
            current_date += relativedelta(months=1)

        # Get monthly totals with proper aggregation
        monthly_spending = {}
        for month in all_months:
            month_total = Transaction.objects.filter(
                bank_account__in=accounts,
                date__year=month.year,
                date__month=month.month
            ).aggregate(total=Sum('amount'))['total'] or 0
            monthly_spending[month] = float(month_total)

        # Convert to list for JSON
        monthly_totals_json = json.dumps([{
            'month': month.strftime('%Y-%m-%d'),
            'total': monthly_spending[month]
        } for month in all_months])

        # Debug print
        print("Monthly spending data:", monthly_spending)
    else:
        monthly_totals_json = '[]'

    return render(request, 'transaction_list.html', {
        'transactions': transactions,
        'accounts': accounts,
        'sort_by': sort_by,
        'deposit_form': deposit_form,
        'withdraw_form': withdraw_form,
        'purchase_form': purchase_form,
        'categories': categories,
        'selected_category': selected_category,
        'category_totals_json': category_totals_json,  # Changed this
        'category_names': category_names,
        'monthly_totals_json': monthly_totals_json,  # Added this
    })