from django.shortcuts import render, redirect, get_object_or_404
from .models import BankAccount
from .forms import BankAccountForm
from transactions.models import Transaction  # Import the Transaction model



# Create your views here.
def dashboard(request):
    #accounts = BankAccount.objects.all()
    accounts = BankAccount.objects.filter(user=request.user)

    # Fetch the 5 most recent transactions for all bank accounts
    recent_transactions = Transaction.objects.filter(bank_account__in=accounts).order_by('-date')[:5]

    return render(request, 'dashboard.html', {
        'accounts': accounts,
        'recent_transactions': recent_transactions  # Pass the recent transactions to the template
    })

def create_account(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            #form.save()
            bank_account = form.save(commit=False)  # Do not save yet
            bank_account.user = request.user
            bank_account.save()
            return redirect('dashboard')
    else:
        form = BankAccountForm()
    return render(request, 'create_account.html', {'form': form})

def view_account(request, account_no):
    #account = get_object_or_404(BankAccount, account_no=account_no)
    account = get_object_or_404(BankAccount, account_no=account_no, user=request.user)
    return render(request, 'view_account.html', {'account': account})



# Edit Bank Account View (FR 5)
def edit_account(request, account_id):
   #account = get_object_or_404(BankAccount, pk=account_id)
   account = get_object_or_404(BankAccount, pk=account_id, user=request.user)  # Ensure the account belongs to the user
   if request.method == 'POST':
       form = BankAccountForm(request.POST, instance=account)
       if form.is_valid():
           form.save()
           return redirect('dashboard')
   else:
       form = BankAccountForm(instance=account)
   return render(request, 'edit_account.html', {'form': form, 'account': account})


# Delete Bank Account View (FR 6)
def delete_account(request, account_id):
   account = get_object_or_404(BankAccount, pk=account_id, user=request.user)
   #account = get_object_or_404(BankAccount, pk=account_id)
   if request.method == 'POST':
       account.delete()
       return redirect('dashboard')
   return render(request, 'delete_account.html', {'account': account})
  
