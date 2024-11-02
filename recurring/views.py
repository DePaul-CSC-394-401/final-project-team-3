from django.shortcuts import render, redirect, get_object_or_404
from .models import RecurringTransaction
from .forms import RecurringTransactionForm

# Create your views here.

def recurring_transaction_list(request):
    recurring_transactions = RecurringTransaction.objects.filter(bank_account__user=request.user)
    return render(request, 'recurring/recurring_transaction_list.html', {
        'recurring_transactions': recurring_transactions,
    })

def add_recurring_transaction(request):
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST)
        if form.is_valid():
            recurring_transaction = form.save(commit=False)
            recurring_transaction.save()
            return redirect('recurring_transaction_list')
    else:
        form = RecurringTransactionForm()
    return render(request, 'recurring/add_recurring_transaction.html', {'form': form})

def edit_recurring_transaction(request, pk):
    recurring_transaction = get_object_or_404(RecurringTransaction, pk=pk)
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, instance=recurring_transaction)
        if form.is_valid():
            form.save()
            return redirect('recurring_transaction_list')
    else:
        form = RecurringTransactionForm(instance=recurring_transaction)
    return render(request, 'recurring/edit_recurring_transaction.html', {'form': form})

def delete_recurring_transaction(request, pk):
    recurring_transaction = get_object_or_404(RecurringTransaction, pk=pk)
    if request.method == 'POST':
        recurring_transaction.delete()
        return redirect('recurring_transaction_list')
    return render(request, 'recurring/delete_recurring_transaction.html', {'transaction': recurring_transaction})


