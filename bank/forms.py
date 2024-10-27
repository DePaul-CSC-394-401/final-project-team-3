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
        # Creates IDs for all BankAccount fields
        super(BankAccountForm, self).__init__(*args, **kwargs)
        self.fields['account_name'].widget.attrs.update({'id': 'id_account_name'})
        self.fields['account_type'].widget.attrs.update({'id': 'id_account_type'})
        self.fields['account_balance'].widget.attrs.update({'id': 'id_account_balance'})
        self.fields['routing_no'].widget.attrs.update({'id': 'id_routing_no'})
        self.fields['account_no'].widget.attrs.update({'id': 'id_account_no'})
        self.fields['card_number'].widget.attrs.update({'id': 'id_card_number'})
        self.fields['name_on_card'].widget.attrs.update({'id': 'id_name_on_card'})
        self.fields['card_institution'].widget.attrs.update({'id': 'id_card_institution'})
        self.fields['finance_institution'].widget.attrs.update({'id': 'id_finance_institution'})

        # Makes the following fields uneditable in the edit_account page 
        if self.instance and self.instance.pk:  
            self.fields['routing_no'].disabled = True
            self.fields['account_no'].disabled = True
            self.fields['account_balance'].disabled = True
            self.fields['account_type'].disabled = True

            account_type = self.instance.account_type

        # Makes the following fields uneditable in the create_account page
        else:
            self.fields['routing_no'].disabled = True
            self.fields['account_no'].disabled = True

            account_type = self.data.get('account_type', '')

        # Establishes what fields are required if "credit" account_type is chosen
        if account_type == 'credit':
            self.fields['account_balance'].required = False
            self.fields['routing_no'].required = False
            self.fields['account_no'].required = False
            self.fields['card_number'].required = True
            self.fields['name_on_card'].required = True
            self.fields['card_institution'].required = True
        else:
            self.fields['account_balance'].required = True
            self.fields['routing_no'].required = True
            self.fields['account_no'].required = True
            self.fields['card_number'].required = False
            self.fields['name_on_card'].required = False
            self.fields['card_institution'].required = False

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get("account_type")

        if account_type == 'credit':
            card_number = cleaned_data.get("card_number")
            name_on_card = cleaned_data.get("name_on_card")
            card_institution = cleaned_data.get("card_institution")

            # Verifies that all CC fields are filled out before creating account
            if not card_number or not name_on_card or not card_institution:
                raise forms.ValidationError(
                    "Credit Card Number, Name on Card, and Card Institution are required for credit accounts."
                )
        else:
            account_balance = cleaned_data.get("account_balance")
            routing_no = cleaned_data.get("routing_no")
            account_no = cleaned_data.get("account_no")

            # Verifies that all non-CC fields are filled out before creating account
            if account_balance is None:
                raise forms.ValidationError(
                    "Account Balance is required for savings or checking accounts."
                )
            
            if not routing_no or not account_no:
                raise forms.ValidationError("Account Balance, Routing Number, and Account Number are required for savings or checking accounts.")