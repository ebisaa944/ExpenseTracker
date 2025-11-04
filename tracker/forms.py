from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Expense, Budget, Category, FinancialGoal, Income, UserProfile, FinancialReport, Notification

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })
    )

def create_default_categories(user):
    """Create default categories for a user if they don't have any"""
    if not Category.objects.filter(user=user).exists():
        default_categories = [
            ('Food & Dining', 'expense', '#FF6B6B'),
            ('Transportation', 'expense', '#4ECDC4'),
            ('Utilities', 'expense', '#45B7D1'),
            ('Housing/Rent', 'expense', '#96CEB4'),
            ('Entertainment', 'expense', '#FFEAA7'),
            ('Shopping', 'expense', '#DDA0DD'),
            ('Healthcare', 'expense', '#98D8C8'),
            ('Education', 'expense', '#F7DC6F'),
            ('Travel', 'expense', '#BB8FCE'),
            ('Salary/Income', 'income', '#82E0AA'),
            ('Other', 'expense', '#85929E')
        ]
        
        for name, cat_type, color in default_categories:
            Category.objects.create(
                user=user,
                name=name,
                type=cat_type,
                color=color
            )

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'category', 'payment_method', 'notes', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes...'}),
            'description': forms.TextInput(attrs={'placeholder': 'Enter expense description'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            create_default_categories(user)
            self.fields['category'].queryset = Category.objects.filter(user=user, type='expense')

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'period', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            create_default_categories(user)
            self.fields['category'].queryset = Category.objects.filter(user=user, type='expense')

class FinancialGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialGoal
        fields = ['name', 'target_amount', 'current_amount', 'deadline', 'description']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your financial goal...'}),
            'target_amount': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'current_amount': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        target_amount = cleaned_data.get('target_amount')
        current_amount = cleaned_data.get('current_amount')
        
        if target_amount and current_amount:
            if current_amount > target_amount:
                raise forms.ValidationError("Current amount cannot exceed target amount.")
        
        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'color', 'icon']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter category name'}),
            'icon': forms.TextInput(attrs={'placeholder': 'Enter icon name (e.g., shopping-cart)'}),
        }

class ExpenseFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="All Categories"
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    payment_method = forms.ChoiceField(
        choices=[('', 'All Methods')] + Expense.PAYMENT_METHODS,
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            create_default_categories(user)
            self.fields['category'].queryset = Category.objects.filter(user=user)

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'source', 'description', 'date', 'is_recurring', 'recurrence_pattern', 'notes']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes...'}),
            'description': forms.TextInput(attrs={'placeholder': 'Enter income description'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Show/hide recurrence pattern based on is_recurring
        if not self.instance.pk:  # Only for new instances
            self.fields['recurrence_pattern'].widget.attrs.update({'class': 'recurrence-field'})
    
    def clean(self):
        cleaned_data = super().clean()
        is_recurring = cleaned_data.get('is_recurring')
        recurrence_pattern = cleaned_data.get('recurrence_pattern')
        
        if is_recurring and recurrence_pattern == 'NONE':
            raise forms.ValidationError("Please select a recurrence pattern for recurring income.")
        
        return cleaned_data

class IncomeFilterForm(forms.Form):
    source = forms.ChoiceField(
        choices=[('', 'All Sources')] + Income.INCOME_SOURCES,
        required=False
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['currency', 'theme', 'language', 'timezone', 'receive_email_notifications', 
                 'receive_budget_alerts', 'monthly_report_enabled']
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'timezone': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add timezone choices dynamically (you can populate this from pytz.common_timezones)
        self.fields['timezone'].choices = [
            ('UTC', 'UTC'),
            ('America/New_York', 'New York'),
            ('America/Los_Angeles', 'Los Angeles'),
            ('Europe/London', 'London'),
            ('Europe/Paris', 'Paris'),
            ('Asia/Tokyo', 'Tokyo'),
            ('Asia/Kolkata', 'India'),
            ('Africa/Addis_Ababa', 'Addis Ababa'),
        ]

class FinancialReportForm(forms.ModelForm):
    report_format = forms.ChoiceField(
        choices=FinancialReport.REPORT_FORMATS,
        initial='PDF',
        widget=forms.RadioSelect
    )
    
    class Meta:
        model = FinancialReport
        fields = ['report_type', 'title', 'description', 'start_date', 'end_date', 'report_format']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter report title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter report description...'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Start date cannot be after end date.")
        
        return cleaned_data

class QuickExpenseForm(forms.ModelForm):
    """Form for quick expense entry (simplified)"""
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'category']
        widgets = {
            'description': forms.TextInput(attrs={
                'placeholder': 'What did you spend on?',
                'class': 'form-control-lg'
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'class': 'form-control-lg'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            create_default_categories(user)
            self.fields['category'].queryset = Category.objects.filter(user=user, type='expense')[:5]  # Limit to top 5 categories

class QuickIncomeForm(forms.ModelForm):
    """Form for quick income entry (simplified)"""
    class Meta:
        model = Income
        fields = ['amount', 'description', 'source']
        widgets = {
            'description': forms.TextInput(attrs={
                'placeholder': 'Income source description',
                'class': 'form-control-lg'
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'class': 'form-control-lg'
            }),
        }

class BudgetAlertForm(forms.Form):
    """Form for configuring budget alerts"""
    alert_threshold = forms.IntegerField(
        min_value=50,
        max_value=100,
        initial=80,
        help_text="Receive alert when spending reaches this percentage of budget",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    receive_email_alerts = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Send budget alerts via email"
    )
    receive_push_alerts = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Show budget alerts in the application"
    )

class RecurringTransactionForm(forms.Form):
    """Form for managing recurring transactions"""
    PROCESS_FREQUENCY = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    
    process_frequency = forms.ChoiceField(
        choices=PROCESS_FREQUENCY,
        initial='DAILY',
        help_text="How often to process recurring transactions"
    )
    auto_process = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Automatically process recurring transactions"
    )
    notify_on_process = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Notify when recurring transactions are processed"
    )

class ExportDataForm(forms.Form):
    """Form for data export options"""
    EXPORT_FORMATS = [
        ('CSV', 'CSV (Excel compatible)'),
        ('JSON', 'JSON'),
        ('PDF', 'PDF Report'),
    ]
    
    DATA_TYPES = [
        ('EXPENSES', 'Expenses Only'),
        ('INCOME', 'Income Only'),
        ('ALL', 'All Financial Data'),
        ('BUDGETS', 'Budgets'),
        ('GOALS', 'Financial Goals'),
    ]
    
    DATE_RANGES = [
        ('CURRENT_MONTH', 'Current Month'),
        ('LAST_MONTH', 'Last Month'),
        ('CURRENT_YEAR', 'Current Year'),
        ('LAST_YEAR', 'Last Year'),
        ('CUSTOM', 'Custom Range'),
    ]
    
    export_format = forms.ChoiceField(
        choices=EXPORT_FORMATS,
        initial='CSV',
        widget=forms.RadioSelect
    )
    data_type = forms.ChoiceField(
        choices=DATA_TYPES,
        initial='ALL',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_range = forms.ChoiceField(
        choices=DATE_RANGES,
        initial='CURRENT_MONTH',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'custom-date-field'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'custom-date-field'})
    )
    include_categories = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Include category information"
    )
    include_notes = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Include notes and descriptions"
    )

class NotificationSettingsForm(forms.ModelForm):
    """Form for notification preferences"""
    class Meta:
        model = UserProfile
        fields = [
            'receive_email_notifications',
            'receive_budget_alerts',
            'monthly_report_enabled'
        ]
        widgets = {
            'receive_email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_budget_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'monthly_report_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BulkDeleteForm(forms.Form):
    """Form for bulk deletion of records"""
    confirm_delete = forms.BooleanField(
        required=True,
        label="I understand this action cannot be undone",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    delete_reason = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Optional reason for deletion...',
            'class': 'form-control'
        })
    )

class DateRangeFilterForm(forms.Form):
    """Generic form for date range filtering"""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")
        
        return cleaned_data