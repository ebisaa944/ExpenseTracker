from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Expense, Budget, FinancialGoal, Income, UserProfile, FinancialReport, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    currency_symbol = serializers.CharField(source='get_currency_symbol', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_username', 'user_email', 'currency', 'currency_symbol',
            'theme', 'language', 'timezone', 'receive_email_notifications',
            'receive_budget_alerts', 'monthly_report_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    name_display = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'name_display', 'type', 'type_display', 'color', 'icon', 'user', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'amount', 'description', 'category', 'category_name', 'category_color',
            'date', 'payment_method', 'payment_method_display', 'notes', 'user', 'user_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class IncomeSerializer(serializers.ModelSerializer):
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    recurrence_pattern_display = serializers.CharField(source='get_recurrence_pattern_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Income
        fields = [
            'id', 'amount', 'source', 'source_display', 'description', 'date',
            'is_recurring', 'recurrence_pattern', 'recurrence_pattern_display',
            'notes', 'user', 'user_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def validate(self, data):
        is_recurring = data.get('is_recurring')
        recurrence_pattern = data.get('recurrence_pattern')
        
        if is_recurring and recurrence_pattern == 'NONE':
            raise serializers.ValidationError("Recurrence pattern is required for recurring income.")
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    spent_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)
    budget_status = serializers.CharField(source='get_budget_status', read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'category_color', 'amount', 'period', 'period_display',
            'start_date', 'end_date', 'user', 'user_username', 'spent_amount', 'remaining_amount',
            'progress_percentage', 'is_over_budget', 'budget_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be greater than zero.")
        return value
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError("End date must be after start date.")
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FinancialGoalSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    amount_needed = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    goal_status = serializers.CharField(source='get_goal_status', read_only=True)
    
    class Meta:
        model = FinancialGoal
        fields = [
            'id', 'name', 'target_amount', 'current_amount', 'deadline', 'description',
            'user', 'user_username', 'progress_percentage', 'days_remaining',
            'is_completed', 'amount_needed', 'goal_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Target amount must be greater than zero.")
        return value
    
    def validate_current_amount(self, value):
        target_amount = self.initial_data.get('target_amount')
        if target_amount:
            try:
                target_value = float(target_amount)
                if value > target_value:
                    raise serializers.ValidationError("Current amount cannot exceed target amount.")
            except (TypeError, ValueError):
                # If conversion fails, skip this validation
                pass
        return value
    
    def validate_deadline(self, value):
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FinancialReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    report_format_display = serializers.CharField(source='get_report_format_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    is_downloadable = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'user', 'user_username', 'report_type', 'report_type_display',
            'report_format', 'report_format_display', 'title', 'description',
            'start_date', 'end_date', 'file_path', 'is_downloadable', 'generated_at'
        ]
        read_only_fields = ['generated_at']

class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_username', 'notification_type', 'notification_type_display',
            'title', 'message', 'is_read', 'related_object_id', 'related_content_type',
            'created_at'
        ]
        read_only_fields = ['created_at']

# Summary and Analytics Serializers
class ExpenseSummarySerializer(serializers.Serializer):
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_savings = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense_count = serializers.IntegerField()
    income_count = serializers.IntegerField()
    savings_rate = serializers.FloatField()

class IncomeSummarySerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    recurring_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    income_by_source = serializers.DictField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
    income_count = serializers.IntegerField()

class CategorySummarySerializer(serializers.Serializer):
    category_name = serializers.CharField()
    category_color = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.FloatField()
    transaction_count = serializers.IntegerField()

class MonthlyTrendSerializer(serializers.Serializer):
    month = serializers.CharField()
    expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    savings = serializers.DecimalField(max_digits=12, decimal_places=2)

class BudgetProgressSerializer(serializers.Serializer):
    category_name = serializers.CharField()
    budget_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    progress_percentage = serializers.FloatField()
    is_over_budget = serializers.BooleanField()
    budget_status = serializers.CharField()

class GoalProgressSerializer(serializers.Serializer):
    goal_name = serializers.CharField()
    target_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    current_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    progress_percentage = serializers.FloatField()
    days_remaining = serializers.IntegerField()
    is_completed = serializers.BooleanField()
    goal_status = serializers.CharField()

class DashboardSummarySerializer(serializers.Serializer):
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_savings = serializers.DecimalField(max_digits=12, decimal_places=2)
    savings_rate = serializers.FloatField()
    budget_alerts_count = serializers.IntegerField()
    active_goals_count = serializers.IntegerField()
    completed_goals_count = serializers.IntegerField()

# Filter Serializers
class ExpenseFilterSerializer(serializers.Serializer):
    category = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    payment_method = serializers.CharField(required=False)
    min_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)

class IncomeFilterSerializer(serializers.Serializer):
    source = serializers.CharField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    is_recurring = serializers.BooleanField(required=False)
    min_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)

class BudgetFilterSerializer(serializers.Serializer):
    category = serializers.IntegerField(required=False)
    period = serializers.CharField(required=False)
    is_over_budget = serializers.BooleanField(required=False)

class GoalFilterSerializer(serializers.Serializer):
    is_completed = serializers.BooleanField(required=False)
    days_remaining_lte = serializers.IntegerField(required=False)  # Less than or equal to
    days_remaining_gte = serializers.IntegerField(required=False)  # Greater than or equal to

class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    
    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data

class ExportRequestSerializer(serializers.Serializer):
    EXPORT_FORMATS = [
        ('CSV', 'CSV'),
        ('JSON', 'JSON'),
        ('PDF', 'PDF'),
    ]
    
    DATA_TYPES = [
        ('EXPENSES', 'Expenses'),
        ('INCOME', 'Income'),
        ('ALL', 'All Financial Data'),
    ]
    
    export_format = serializers.ChoiceField(choices=EXPORT_FORMATS)
    data_type = serializers.ChoiceField(choices=DATA_TYPES)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    include_categories = serializers.BooleanField(default=True)
    include_notes = serializers.BooleanField(default=True)

class RecurringTransactionRequestSerializer(serializers.Serializer):
    process_frequency = serializers.ChoiceField(choices=[
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ])
    auto_process = serializers.BooleanField(default=True)
    notify_on_process = serializers.BooleanField(default=True)

class NotificationMarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )

class BulkDeleteSerializer(serializers.Serializer):
    model_type = serializers.ChoiceField(choices=[
        ('EXPENSE', 'Expense'),
        ('INCOME', 'Income'),
        ('BUDGET', 'Budget'),
        ('GOAL', 'FinancialGoal'),
    ])
    object_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    confirm_delete = serializers.BooleanField(required=True)

# API Response Serializers
class ApiResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    data = serializers.DictField(required=False)
    errors = serializers.ListField(child=serializers.DictField(), required=False)

class PaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(required=False, allow_null=True)
    previous = serializers.URLField(required=False, allow_null=True)
    results = serializers.ListField(child=serializers.DictField())

# Chart Data Serializers
class ChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=serializers.DictField())

class PieChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    colors = serializers.ListField(child=serializers.CharField())

class TimeSeriesDataSerializer(serializers.Serializer):
    dates = serializers.ListField(child=serializers.DateField())
    values = serializers.ListField(child=serializers.FloatField())