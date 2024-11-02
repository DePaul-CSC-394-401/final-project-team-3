from django import forms
from .models import RecurringTransaction

class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        fields = ['name', 'amount', 'frequency', 'bank_account', 'start_date', 'end_date', 'category']

    def __init__(self, *args, **kwargs):
        # Pop the user from kwargs
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter bank account choices to only include accounts owned by the user
        if user:
            self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)

        # Add Bootstrap classes (optional)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'