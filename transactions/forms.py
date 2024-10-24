from django import forms
from .models import Transaction
from bank.models import BankAccount

class BaseTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['name', 'description', 'date', 'amount', 'bank_account']

class PurchaseForm(BaseTransactionForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # All accounts are available for purchases
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)

class WithdrawForm(BaseTransactionForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # Only non-credit accounts should be available for withdraw
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user).exclude(account_type='credit')

class DepositForm(BaseTransactionForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # All accounts are available for deposits
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)
