from django import forms
from .models import Transaction
from bank.models import BankAccount


class BaseTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['name', 'description', 'date', 'amount', 'bank_account', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category field required
        self.fields['category'].required = True


class PurchaseForm(BaseTransactionForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # All accounts are available for purchases
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)

        # Limit categories for purchases - exclude categories that don't make sense for purchases
        self.fields['category'].choices = [
            choice for choice in Transaction.TRANSACTION_CATEGORIES
            if choice[0] not in ['credit', 'income', 'transfer']
        ]


class WithdrawForm(BaseTransactionForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # Only non-credit accounts should be available for withdraw
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user).exclude(account_type='credit')

        # Limit categories for withdrawals
        self.fields['category'].choices = [
            ('transfer', 'Transfer'),
            ('other', 'Other')
        ]


class DepositForm(BaseTransactionForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # All accounts are available for deposits
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)

        # Limit categories for deposits
        self.fields['category'].choices = [
            ('income', 'Income'),
            ('transfer', 'Transfer'),
            ('credit', 'Credit Card Payment'),
            ('other', 'Other')
        ]