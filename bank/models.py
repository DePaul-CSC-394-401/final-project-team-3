from django.db import models
import random


class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('checking', 'Checking Account'),
        ('credit', 'Credit Card'),
    ]

    FINANCE_INSTITUTIONS = [
        ('JPM', 'JPMorgan Chase'),
        ('BOA', 'Bank of America'),
        ('WF', 'Wells Fargo'),
        ('CITI', 'Citi Bank'),
        ('PNC', 'PNC Bank'),
        ('US', 'U.S. Bank'),
        ('GSB', 'Goldman Sachs Bank'),
        ('TRU', 'Truist Bank'),
        ('CAP1', 'Capital One'),
        ('TD', 'TD Bank'),
    ]

    CC_INSTITUTIONS = [
        ('AMEX', 'American Express'),
        ('DISC', 'Discover'),
        ('MASTER', 'Mastercard'),
        ('VISA', 'Visa'),
    ]

    def generate_account_number():
        while True:
            account_no = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            if not BankAccount.objects.filter(account_no=account_no).exists():
                return account_no

    def generate_routing_number():
        while True:
            routing_no = ''.join([str(random.randint(0, 9)) for _ in range(10)])

            if not BankAccount.objects.filter(routing_no=routing_no).exists():
                return routing_no

    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    account_no = models.CharField(max_length=6, unique=True, default=generate_account_number)
    routing_no = models.CharField(max_length=10, unique=True, default=generate_routing_number)

    finance_institution = models.CharField(max_length=20, choices=FINANCE_INSTITUTIONS, default='NOT DISCLOSED')

    card_number = models.CharField(max_length=16, blank=True, null=True)
    name_on_card = models.CharField(max_length=100, blank=True, null=True)
    card_institution = models.CharField(max_length=20, choices=CC_INSTITUTIONS, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Check if the account is being created (i.e., it doesn't have an ID yet)
        if not self.pk and self.account_type == 'credit':
            # If it's a credit account being created, set the balance to 0
            self.account_balance = 0.00

            # Validate that all required card fields are present
            if not self.card_number or not self.name_on_card or not self.card_institution:
                raise ValueError(
                    "Credit Card Number, Name on Card, and Card Institution are required for credit accounts.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account_name} | {self.account_type.title()} | {self.account_balance} | {self.account_no} | {self.routing_no} | {self.finance_institution} | {self.card_number} | {self.name_on_card} | {self.card_institution}"
