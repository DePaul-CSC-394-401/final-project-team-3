from django.shortcuts import render, redirect
from .models import Transaction
from .forms import PurchaseForm, WithdrawForm, DepositForm
from .models import BankAccount
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json
from django.db.models import Count, Sum, Min, Max
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
    # Get user's bank accounts
    accounts = BankAccount.objects.filter(user=request.user)

    # Fetch all transactions for the user's accounts by default
    transactions = Transaction.objects.filter(bank_account__in=accounts)

    # Get the sort_by query parameter
    sort_by = request.GET.get('sort_by', 'date')

    # Filter by selected account
    selected_account = request.GET.get('account')
    if sort_by == 'account' and selected_account:
        transactions = transactions.filter(bank_account__id=selected_account)

    # Filter by selected date
    selected_date = request.GET.get('date')
    if sort_by == 'date' and selected_date:
        transactions = transactions.filter(date=selected_date)

    # Filter by category
    selected_category = request.GET.get('category')
    if selected_category:
        transactions = transactions.filter(category=selected_category)

    # Default sorting
    transactions = transactions.order_by('-date')

    # Forms
    deposit_form = DepositForm(user=request.user)
    withdraw_form = WithdrawForm(user=request.user)
    purchase_form = PurchaseForm(user=request.user)

    # Get date range for charts
    date_range = Transaction.objects.filter(bank_account__in=accounts).aggregate(
        min_date=Min('date'),
        max_date=Max('date')
    )

    if date_range['min_date'] and date_range['max_date']:
        # Create a list of all months between min and max date
        # List is used to make the x-axis
        current_date = date_range['min_date'].replace(day=1)
        end_date = date_range['max_date'].replace(day=1)
        all_months = []

        while current_date <= end_date:
            all_months.append(current_date)
            current_date += relativedelta(months=1)

        # Create data for each category
        # Go thru each month and add it to the list of each month
        # Add totals to the categories to that list
        category_monthly_data = {}
        for category_code, category_name in Transaction.TRANSACTION_CATEGORIES:
            monthly_spending = {}
            for month in all_months:
                month_total = Transaction.objects.filter(
                    bank_account__in=accounts,
                    category=category_code,
                    date__year=month.year,
                    date__month=month.month
                ).aggregate(total=Sum('amount'))['total'] or 0
                monthly_spending[month] = float(month_total)

            category_monthly_data[category_code] = {
                'name': category_name,
                'data': [monthly_spending[month] for month in all_months]
            }

        # Prepare the JSON data for the line chart
        chart_data = {
            'labels': [month.strftime('%Y-%m-%d') for month in all_months],
            'datasets': []
        }

        # Define colors
        colors = [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0',
            '#C9CBCF',
            '#9966FF',
            '#FF9F40',
            '#2ECC71',
            '#E74C3C',
            '#8E44AD',
            '#16A085',
            '#D35400',
            '#27AE60',
            '#3498DB',
        ]


        # Create lines for each category
        # Start with all lines hidden except total
        # Keep points for category lines
        for i, (category_code, data) in enumerate(category_monthly_data.items()):
            category_color = colors[i] if i < len(colors) else colors[i % len(colors)]
            chart_data['datasets'].append({
                'label': data['name'],
                'data': data['data'],
                'borderColor': category_color,
                'backgroundColor': category_color,
                'hidden': True,  
                'fill': False,
                'order': 1,
                'pointRadius': 0,  
                'pointHoverRadius': 6
            })

        # Add total spending line
        total_spending = [sum(category_monthly_data[cat]['data'][i]
                              for cat in category_monthly_data.keys())
                          for i in range(len(all_months))]

        chart_data['datasets'].append({
            'label': 'Total',
            'data': total_spending,
            'borderColor': 'rgba(0, 0, 0, 0.7)', 
            'backgroundColor': 'rgba(0, 0, 0, 0.2)', 
            'fill': True, 
            'hidden': False, 
            'order': 2,  
            'pointRadius': 0, 
            'pointHoverRadius': 0
        })


        monthly_totals_json = json.dumps(chart_data)
    else:
        monthly_totals_json = '[]'

    # Get the transactions for the pie chart
    all_transactions = Transaction.objects.filter(bank_account__in=accounts)

    # Figure out the categories for pie chart
    category_totals_dict = {code: 0 for code, _ in Transaction.TRANSACTION_CATEGORIES}

    # Get actual totals from transactions
    category_aggregation = all_transactions.values('category').annotate(
    total=Sum('amount')
)

    # Update dictionary with actual values
    for item in category_aggregation:
        if item['category'] in category_totals_dict:
            category_totals_dict[item['category']] = float(item['total'])

    # Prep data for json in the same order as transactions_categories
    category_totals_json = json.dumps([
        {
            'category': category_code,
            'total': category_totals_dict[category_code]
        }
        for category_code, _ in Transaction.TRANSACTION_CATEGORIES
    ])

    # Get all category choices from the transaction model
    category_choices = Transaction.TRANSACTION_CATEGORIES

    context = {
        'transactions': transactions,
        'accounts': accounts,
        'sort_by': sort_by,
        'deposit_form': deposit_form,
        'withdraw_form': withdraw_form,
        'purchase_form': purchase_form,
        'categories': category_choices,
        'selected_category': selected_category,
        'monthly_totals_json': monthly_totals_json,
        'category_totals_json': category_totals_json,
    }

    return render(request, 'transaction_list.html', context)