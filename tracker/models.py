from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Expense(models.Model):
    """
    Represents a single financial transaction (expense or income).
    Amount is stored as Decimal for precision in financial calculations.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='expenses',
        help_text="The user who recorded this transaction."
    )
    title = models.CharField(max_length=255, help_text="A short description of the transaction.")
    
    # DecimalField is crucial for financial data (prevents floating point errors)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="The amount of the transaction. Positive for expense, negative for income."
    )
    
    # Use a fixed set of choices for categories
    CATEGORY_CHOICES = [
        ('FOOD', 'Food & Dining'),
        ('HOUSE', 'Housing'),
        ('TRANS', 'Transportation'),
        ('ENTER', 'Entertainment'),
        ('OTHER', 'Other'),
        ('INCOME', 'Income (Deposit/Wage)'),
    ]
    category = models.CharField(
        max_length=10, # <-- FIXED: Increased max_length to accommodate the 'INCOME' key (6 characters)
        choices=CATEGORY_CHOICES, 
        default='OTHER',
        help_text="The category of the transaction."
    )
    
    date = models.DateField(help_text="The date the transaction occurred.")
    
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the record was created.")

    def __str__(self):
        return f"{self.date} - {self.title} ({self.amount})"

    class Meta:
        ordering = ['-date', '-timestamp'] # Default sorting: newest first
        verbose_name_plural = "Expenses"
