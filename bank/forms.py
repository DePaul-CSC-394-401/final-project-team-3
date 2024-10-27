from django import forms
from .models import BankAccount


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = [
            'account_name', 'account_type', 'account_balance', 'account_no', 
            'routing_no', 'finance_institution', 'card_number', 
            'name_on_card', 'card_institution'
        ]
        widgets = {
            'account_type': forms.Select(choices=BankAccount.ACCOUNT_TYPES),
            'finance_institution': forms.Select(choices=BankAccount.FINANCE_INSTITUTIONS),
            'card_institution': forms.Select(choices=BankAccount.CC_INSTITUTIONS),
        }

    def __init__(self, *args, **kwargs):
        super(BankAccountForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:  
            self.fields['routing_no'].disabled = True
            self.fields['account_no'].disabled = True
            self.fields['account_balance'].disabled = True
            self.fields['account_type'].disabled = True
        else:
            self.fields['routing_no'].disabled = True
            self.fields['account_no'].disabled = True

        if self.instance.account_type == 'credit':
            self.fields['card_number'].required = True
            self.fields['name_on_card'].required = True
            self.fields['card_institution'].required = True

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get("account_type")

        if account_type == 'credit':
            card_number = cleaned_data.get("card_number")
            name_on_card = cleaned_data.get("name_on_card")
            card_institution = cleaned_data.get("card_institution")

            if not card_number or not name_on_card or not card_institution:
                raise forms.ValidationError(
                    "Credit Card Number, Name on Card, and Card Institution are required for credit accounts."
                )

