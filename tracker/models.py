from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse

class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    CATEGORY_CHOICES = [
        ('FOOD', 'Food & Dining'),
        ('TRANSPORT', 'Transportation'),
        ('UTILITIES', 'Utilities'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('SHOPPING', 'Shopping'),
        ('HEALTHCARE', 'Healthcare'),
        ('EDUCATION', 'Education'),
        ('TRAVEL', 'Travel'),
        ('INCOME', 'Income'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='expense')
    color = models.CharField(max_length=7, default='#007bff')
    icon = models.CharField(max_length=50, default='receipt')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return self.get_name_display()

class Expense(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('DIGITAL', 'Digital Wallet'),
        ('BANK', 'Bank Transfer'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    description = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='CARD')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.description} - ${self.amount}"
    
    def get_absolute_url(self):
        return reverse('expense_list')

class Budget(models.Model):
    PERIOD_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='MONTHLY')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        unique_together = ['user', 'category', 'period']
    
    def __str__(self):
        return f"{self.category} - ${self.amount} ({self.period})"
    
    def spent_amount(self):
        from django.db.models import Sum
        result = Expense.objects.filter(
            user=self.user,
            category=self.category,
            date__date__gte=self.start_date,
            date__date__lte=self.end_date if self.end_date else timezone.now().date()
        ).aggregate(Sum('amount'))['amount__sum']
        return result or 0
    
    def remaining_amount(self):
        return self.amount - self.spent_amount()
    
    def progress_percentage(self):
        if self.amount > 0:
            return min((self.spent_amount() / self.amount) * 100, 100)
        return 0

class FinancialGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['deadline']
    
    def __str__(self):
        return self.name
    
    def progress_percentage(self):
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0
    
    def days_remaining(self):
        from datetime import date
        remaining = (self.deadline - date.today()).days
        return max(remaining, 0)