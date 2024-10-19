from django.db import models

# Create your models here.
class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('checking', 'Checking Account'),
    ]

    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def deposit(self, amount):
        self.account_balance += amount
        self.save()

    def withdraw(self, amount):
        if self.account_balance >= amount:
            self.account_balance -= amount
            self.save() 

    def __str__(self):
        return f"{self.account_name} | {self.account_type.title()} | {self.account_balance}"
    
