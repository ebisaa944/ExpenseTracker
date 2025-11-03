from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Expense, Budget, FinancialGoal

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']

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

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    spent_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'category_color', 'amount', 'period', 'period_display',
            'start_date', 'end_date', 'user', 'user_username', 'spent_amount', 'remaining_amount',
            'progress_percentage', 'created_at', 'updated_at'
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
    
    class Meta:
        model = FinancialGoal
        fields = [
            'id', 'name', 'target_amount', 'current_amount', 'deadline', 'description',
            'user', 'user_username', 'progress_percentage', 'days_remaining',
            'created_at', 'updated_at'
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

# Summary and Analytics Serializers
class ExpenseSummarySerializer(serializers.Serializer):
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_savings = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense_count = serializers.IntegerField()
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

class BudgetProgressSerializer(serializers.Serializer):
    category_name = serializers.CharField()
    budget_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    progress_percentage = serializers.FloatField()
    is_over_budget = serializers.BooleanField()

# Filter Serializers
class ExpenseFilterSerializer(serializers.Serializer):
    category = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    payment_method = serializers.CharField(required=False)
    min_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)

class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    
    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data