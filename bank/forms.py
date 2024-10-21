from django import forms
from .models import BankAccount


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['account_name', 'account_type', 'account_balance', 'account_no', 'routing_no', 'finance_institution', 'card_number', 'name_on_card', 'card_institution']
        widgets = {
            'account_type': forms.Select(choices=BankAccount.ACCOUNT_TYPES),
            'finance_institution': forms.Select(choices=BankAccount.FINANCE_INSTITUTIONS),
            'card_institution': forms.Select(choices=BankAccount.CC_INSTITUTIONS),
        }