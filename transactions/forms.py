from django import forms
from .models import Transaction
from .models import BankAccount

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'name', 'description', 'date', 'amount', 'bank_account']
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            # Filter the bank accounts to only include those associated with the logged-in user
            self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)
