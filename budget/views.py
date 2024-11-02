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

            category = form.cleaned_data.get('category')
            account = form.cleaned_data['account']
            period_type = form.cleaned_data['period_type']
            #budget_type = form.cleaned_data['budget_type']  # Added this line
            
            # Check for account-based budget if 'account' is provided
            if account:
                existing_budget = Budget.objects.filter(
                    user=request.user,
                    account=account,
                    period_type=period_type
                ).exists()

                if existing_budget:
                    messages.error(request, 'A budget with this account and period type already exists.')
                    #return render(request, 'budget_form.html', {'form': form, 'title': 'Create Budget'})
                    return redirect('budget:budget_list')
            
            # Check for category-based budget if 'category' is provided
            elif category:
                existing_budget = Budget.objects.filter(
                    user=request.user,
                    category=category,
                    period_type=period_type
                ).exists()

                if existing_budget:
                    messages.error(request, 'A budget with this category and period type already exists.')
                    #return render(request, 'budget_form.html', {'form': form, 'title': 'Create Budget'})
                    return redirect('budget:budget_list')


            print('form.is_valid')
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budget:budget_list')
    else:
        form = BudgetForm(user=request.user)

    print("Rendering form")
    # Debug: print the form's HTML representation
    print(form.as_p())  # You can also use as_table() or as_ul()
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
            return redirect('budget:budget_list')
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
        return redirect('budget:budget_list')

    return render(request, 'budget_confirm_delete.html', {'budget': budget})