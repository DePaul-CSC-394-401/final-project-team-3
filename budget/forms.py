# budget/forms.py
from django import forms
from .models import Budget
from bank.models import BankAccount


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'budget_type', 'account', 'category',
                  'allocation_type', 'allocation_amount', 'period_type', 'start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Filter account choices to user's accounts only
        self.fields['account'].queryset = BankAccount.objects.filter(user=user)

        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        # Set up dynamic field dependencies
        self.fields['account'].required = False
        self.fields['category'].required = False

        # Add help text
        self.fields['allocation_amount'].help_text = 'Enter amount in dollars or percentage (0-100)'

    def clean(self):
        cleaned_data = super().clean()
        budget_type = cleaned_data.get('budget_type')
        account = cleaned_data.get('account')
        category = cleaned_data.get('category')
        allocation_type = cleaned_data.get('allocation_type')
        allocation_amount = cleaned_data.get('allocation_amount')

        if budget_type == 'account' and not account:
            raise forms.ValidationError('Account is required for account-based budgets')

        if budget_type == 'category' and not category:
            raise forms.ValidationError('Category is required for category-based budgets')

        if allocation_type == 'percentage' and allocation_amount:
            if allocation_amount > 100 or allocation_amount < 0:
                raise forms.ValidationError('Percentage must be between 0 and 100')

        return cleaned_data