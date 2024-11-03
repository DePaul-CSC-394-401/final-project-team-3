from django.contrib.auth.models import User
from django.db import models
from bank.models import BankAccount
import random
import string
from django.utils import timezone

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('withdraw', 'Withdraw'),
        ('deposit', 'Deposit'),
    ]

    TRANSACTION_CATEGORIES = [
        ('bills', 'Bills & Utilities'),
        ('food', 'Food & Dining'),
        ('shopping', 'Shopping'),
        ('transport', 'Transportation'),
        ('entertainment', 'Entertainment'),
        ('health', 'Healthcare'),
        ('credit', 'Credit Card Payment'),
        ('income', 'Income'),
        ('transfer', 'Transfer'),
        ('other', 'Other'),
    ]

    def generate_transaction_id():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    transaction_id = models.CharField(max_length=10, unique=True, default=generate_transaction_id, editable=False)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=TRANSACTION_CATEGORIES, default='other')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bank_account = models.ForeignKey(BankAccount, to_field='account_no', on_delete=models.CASCADE)
    #user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name} | {self.transaction_type.title()} | {self.bank_account} | ${self.amount}"
