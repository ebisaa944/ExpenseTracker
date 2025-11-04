from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse
from datetime import date

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
        return reverse('tracker:expense_list')

class Income(models.Model):
    INCOME_SOURCES = [
        ('SALARY', 'Salary'),
        ('FREELANCE', 'Freelance Work'),
        ('BUSINESS', 'Business Income'),
        ('INVESTMENT', 'Investment'),
        ('RENTAL', 'Rental Income'),
        ('GIFT', 'Gift'),
        ('OTHER', 'Other Income'),
    ]
    
    RECURRENCE_PATTERNS = [
        ('NONE', 'None'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    source = models.CharField(max_length=20, choices=INCOME_SOURCES, default='SALARY')
    description = models.CharField(max_length=200)
    date = models.DateTimeField(default=timezone.now)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(
        max_length=10, 
        choices=RECURRENCE_PATTERNS, 
        default='NONE'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_source_display()} - ${self.amount}"
    
    def get_absolute_url(self):
        return reverse('tracker:income_list')
    
    def should_process_recurrence(self, current_date=None):
        """Check if this recurring income should be processed for the given date"""
        if not self.is_recurring or self.recurrence_pattern == 'NONE':
            return False
            
        if current_date is None:
            current_date = timezone.now().date()
            
        last_occurrence = self.date.date()
        
        if self.recurrence_pattern == 'DAILY':
            return (current_date - last_occurrence).days >= 1
        elif self.recurrence_pattern == 'WEEKLY':
            return (current_date - last_occurrence).days >= 7
        elif self.recurrence_pattern == 'MONTHLY':
            return (current_date.year != last_occurrence.year or 
                   current_date.month != last_occurrence.month)
        elif self.recurrence_pattern == 'YEARLY':
            return current_date.year != last_occurrence.year
            
        return False

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
    
    def is_over_budget(self):
        """Check if budget is exceeded"""
        return self.spent_amount() > self.amount
    
    def get_budget_status(self):
        """Get budget status for alerts"""
        spent = self.spent_amount()
        percentage = self.progress_percentage()
        
        if percentage >= 100:
            return 'exceeded'
        elif percentage >= 80:
            return 'warning'
        elif percentage >= 50:
            return 'info'
        else:
            return 'good'

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
        remaining = (self.deadline - date.today()).days
        return max(remaining, 0)
    
    def is_completed(self):
        """Check if goal is completed"""
        return self.current_amount >= self.target_amount
    
    def amount_needed(self):
        """Calculate amount needed to reach goal"""
        return max(self.target_amount - self.current_amount, 0)
    
    def get_goal_status(self):
        """Get goal status for display"""
        if self.is_completed():
            return 'completed'
        elif self.days_remaining() <= 7:
            return 'urgent'
        elif self.days_remaining() <= 30:
            return 'warning'
        else:
            return 'active'

class FinancialReport(models.Model):
    """Model to store generated financial reports"""
    REPORT_TYPES = [
        ('MONTHLY', 'Monthly Report'),
        ('YEARLY', 'Yearly Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    REPORT_FORMATS = [
        ('PDF', 'PDF'),
        ('CSV', 'CSV'),
        ('EXCEL', 'Excel'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES, default='MONTHLY')
    report_format = models.CharField(max_length=10, choices=REPORT_FORMATS, default='PDF')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    file_path = models.CharField(max_length=500, blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('tracker:financial_reports')
    
    def is_downloadable(self):
        """Check if report file is available for download"""
        return bool(self.file_path and self.file_path.strip())

class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPES = [
        ('BUDGET_ALERT', 'Budget Alert'),
        ('GOAL_REMINDER', 'Goal Reminder'),
        ('RECURRING_INCOME', 'Recurring Income'),
        ('SYSTEM', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_content_type = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()

class UserProfile(models.Model):
    """Extended user profile for additional settings"""
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('ETB', 'Ethiopian Birr (Br)'),
        ('INR', 'Indian Rupee (₹)'),
        ('JPY', 'Japanese Yen (¥)'),
    ]
    
    THEME_CHOICES = [
        ('LIGHT', 'Light Theme'),
        ('DARK', 'Dark Theme'),
        ('AUTO', 'Auto (System)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    theme = models.CharField(max_length=5, choices=THEME_CHOICES, default='LIGHT')
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    receive_email_notifications = models.BooleanField(default=True)
    receive_budget_alerts = models.BooleanField(default=True)
    monthly_report_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile - {self.user.username}"
    
    def get_currency_symbol(self):
        """Get currency symbol for display"""
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'ETB': 'Br',
            'INR': '₹',
            'JPY': '¥',
        }
        return currency_symbols.get(self.currency, '$')

# Signal to create user profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()