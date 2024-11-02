from django.db import models
from bank.models import BankAccount
from django.utils import timezone

# Create your models here.

class RecurringTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    transaction_type = models.CharField(max_length=10, default='purchase', editable=False)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.frequency}) - ${self.amount}"

    class Meta:
        ordering = ['-start_date']