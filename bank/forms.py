from django import forms
from .models import BankAccount


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['account_name', 'account_type', 'account_balance']
        widgets = {
            'account_type': forms.Select(choices=BankAccount.ACCOUNT_TYPES),
        }

class DepositForm(forms.Form):
    account_id = forms.IntegerField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

class WithdrawForm(forms.Form):
    account_id = forms.IntegerField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2)