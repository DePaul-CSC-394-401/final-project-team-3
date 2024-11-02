from django import forms
from .models import RecurringTransaction

class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        fields = ['name', 'amount', 'frequency', 'bank_account', 'start_date', 'end_date']