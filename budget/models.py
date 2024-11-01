from django.db import models
from django.contrib.auth.models import User
from bank.models import BankAccount
from transactions.models import Transaction
from decimal import Decimal
from django.utils import timezone
from datetime import datetime


class Budget(models.Model):
    BUDGET_TYPES = [
        ('account', 'Account Based'),
        ('category', 'Category Based'),
    ]

    ALLOCATION_TYPES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Balance'),
    ]

    PERIOD_TYPES = [
        ('monthly', 'Monthly'),
        # Could add other periods in the future:
        # ('weekly', 'Weekly'),
        # ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    budget_type = models.CharField(max_length=10, choices=BUDGET_TYPES)

    # These fields will be used based on budget_type
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Required for account-based budgets"
    )
    category = models.CharField(
        max_length=20,
        choices=Transaction.TRANSACTION_CATEGORIES,
        null=True,
        blank=True,
        help_text="Required for category-based budgets"
    )

    allocation_type = models.CharField(max_length=10, choices=ALLOCATION_TYPES)
    allocation_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Fixed amount or percentage depending on allocation type"
    )

    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_TYPES,
        default='monthly'
    )
    start_date = models.DateField(default=timezone.now)

    # Auto-updated fields
    current_amount_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ['user', 'account', 'period_type'],  # One budget per account per period
            ['user', 'category', 'period_type']  # One budget per category per period
        ]

    def calculate_budget_limit(self):
        """Calculate the total budget limit based on allocation type"""
        if self.allocation_type == 'fixed':
            return self.allocation_amount
        elif self.allocation_type == 'percentage':
            if self.budget_type == 'account' and self.account:
                return (self.account.account_balance * self.allocation_amount) / Decimal('100.0')
            return Decimal('0.00')
        return Decimal('0.00')

    def update_amount_spent(self):
        """Update the current amount spent for this budget period"""
        # Get the start of the current period
        now = timezone.now()
        if self.period_type == 'monthly':
            period_start = datetime(now.year, now.month, 1).date()

        # Query relevant transactions
        if self.budget_type == 'account':
            transactions = Transaction.objects.filter(
                bank_account=self.account,
                date__gte=period_start,
                date__lte=now
            )
        else:  # category-based
            transactions = Transaction.objects.filter(
                bank_account__user=self.user,
                category=self.category,
                date__gte=period_start,
                date__lte=now
            )

        # Calculate total spent
        total_spent = sum(t.amount for t in transactions)
        self.current_amount_spent = total_spent
        self.save()

    def get_remaining_budget(self):
        """Calculate remaining budget for the period"""
        return self.calculate_budget_limit() - self.current_amount_spent

    def get_percentage_used(self):
        """Calculate percentage of budget used"""
        limit = self.calculate_budget_limit()
        if limit > 0:
            return (self.current_amount_spent / limit) * 100
        return 0

    def __str__(self):
        if self.budget_type == 'account':
            return f"{self.name} - {self.account.account_name} Budget"
        return f"{self.name} - {self.get_category_display()} Budget"

    def save(self, *args, **kwargs):
        # Validate that either account or category is set based on budget_type
        if self.budget_type == 'account' and not self.account:
            raise ValueError("Account-based budgets must have an account specified")
        if self.budget_type == 'category' and not self.category:
            raise ValueError("Category-based budgets must have a category specified")

        # Ensure allocation_amount is positive
        if self.allocation_amount <= 0:
            raise ValueError("Allocation amount must be positive")

        # For percentage allocations, ensure it's <= 100
        if self.allocation_type == 'percentage' and self.allocation_amount > 100:
            raise ValueError("Percentage allocation cannot exceed 100%")

        super().save(*args, **kwargs)