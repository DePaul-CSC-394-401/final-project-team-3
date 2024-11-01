# budget/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Budget
from .forms import BudgetForm
from decimal import Decimal


@login_required
def budget_list(request):
    """Display list of all budgets for the user"""
    budgets = Budget.objects.filter(user=request.user)

    # Update amounts spent for all budgets
    for budget in budgets:
        budget.update_amount_spent()

    context = {
        'budgets': budgets,
        'account_budgets': budgets.filter(budget_type='account'),
        'category_budgets': budgets.filter(budget_type='category'),
    }
    return render(request, 'budget_list.html', context)


@login_required
def budget_detail(request, pk):
    """Display detailed view of a specific budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    budget.update_amount_spent()

    context = {
        'budget': budget,
        'limit': budget.calculate_budget_limit(),
        'remaining': budget.get_remaining_budget(),
        'percentage_used': budget.get_percentage_used(),
    }
    return render(request, 'budget_detail.html', context)


@login_required
def budget_create(request):
    """Create a new budget"""
    print('views.py budget_create')
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            print('form.is_valid')
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)

    return render(request, 'budget_form.html', {'form': form, 'title': 'Create Budget'})


@login_required
def budget_edit(request, pk):
    """Edit an existing budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)

    return render(request, 'budget_form.html', {'form': form, 'title': 'Edit Budget'})


@login_required
def budget_delete(request, pk):
    """Delete a budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('budget_list')

    return render(request, 'budget_confirm_delete.html', {'budget': budget})