from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Category, Expense, Budget, FinancialGoal
from .serializers import (
    CategorySerializer, ExpenseSerializer, BudgetSerializer, FinancialGoalSerializer,
    ExpenseSummarySerializer, CategorySummarySerializer, MonthlyTrendSerializer,
    BudgetProgressSerializer, ExpenseFilterSerializer, DateRangeSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).select_related('category').order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get expense summary for the current user"""
        try:
            today = timezone.now()
            start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Monthly totals with proper aggregation handling
            monthly_expenses_data = self.get_queryset().filter(
                category__type='expense',
                date__gte=start_of_month
            ).aggregate(total=Sum('amount'))
            monthly_expenses = monthly_expenses_data['total'] or 0
            
            monthly_income_data = self.get_queryset().filter(
                category__type='income',
                date__gte=start_of_month
            ).aggregate(total=Sum('amount'))
            monthly_income = monthly_income_data['total'] or 0
            
            # Counts
            expense_count = self.get_queryset().filter(category__type='expense').count()
            income_count = self.get_queryset().filter(category__type='income').count()
            
            summary = {
                'total_expenses': monthly_expenses,
                'total_income': monthly_income,
                'net_savings': monthly_income - monthly_expenses,
                'expense_count': expense_count,
                'income_count': income_count,
            }
            
            serializer = ExpenseSummarySerializer(summary)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': f'Error generating summary: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get expenses grouped by category"""
        try:
            today = timezone.now()
            start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            category_data = self.get_queryset().filter(
                category__type='expense',
                date__gte=start_of_month
            ).values('category__name', 'category__color').annotate(
                total_amount=Sum('amount'),
                transaction_count=Count('id')
            ).order_by('-total_amount')
            
            # Convert to list and handle empty case
            category_list = list(category_data)
            total_expenses = sum(item['total_amount'] for item in category_list if item['total_amount'])
            
            result = []
            for item in category_list:
                percentage = (item['total_amount'] / total_expenses * 100) if total_expenses > 0 else 0
                result.append({
                    'category_name': item['category__name'],
                    'category_color': item['category__color'],
                    'total_amount': item['total_amount'] or 0,
                    'percentage': round(percentage, 2),
                    'transaction_count': item['transaction_count']
                })
            
            serializer = CategorySummarySerializer(result, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': f'Error generating category data: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def filter(self, request):
        """Filter expenses with various criteria"""
        try:
            filter_serializer = ExpenseFilterSerializer(data=request.data)
            if not filter_serializer.is_valid():
                return Response(filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = self.get_queryset()
            filters = filter_serializer.validated_data
            
            if filters.get('category'):
                queryset = queryset.filter(category_id=filters['category'])
            if filters.get('start_date'):
                # Fix: Proper datetime filtering with timezone
                start_datetime = timezone.make_aware(datetime.combine(filters['start_date'], datetime.min.time()))
                queryset = queryset.filter(date__gte=start_datetime)
            if filters.get('end_date'):
                end_datetime = timezone.make_aware(datetime.combine(filters['end_date'], datetime.max.time()))
                queryset = queryset.filter(date__lte=end_datetime)
            if filters.get('payment_method'):
                queryset = queryset.filter(payment_method=filters['payment_method'])
            if filters.get('min_amount'):
                queryset = queryset.filter(amount__gte=filters['min_amount'])
            if filters.get('max_amount'):
                queryset = queryset.filter(amount__lte=filters['max_amount'])
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': f'Error filtering expenses: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def progress(self, request):
        """Get budget progress for all categories"""
        try:
            budgets = self.get_queryset()
            
            progress_data = []
            for budget in budgets:
                spent = budget.spent_amount()
                progress_data.append({
                    'category_name': budget.category.get_name_display(),  # Use display name
                    'budget_amount': budget.amount,
                    'spent_amount': spent,
                    'remaining_amount': budget.remaining_amount(),
                    'progress_percentage': budget.progress_percentage(),
                    'is_over_budget': spent > budget.amount
                })
            
            serializer = BudgetProgressSerializer(progress_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': f'Error generating budget progress: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FinancialGoalViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialGoalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FinancialGoal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update the current amount for a financial goal"""
        try:
            goal = self.get_object()
            current_amount = request.data.get('current_amount')
            
            if current_amount is None:
                return Response(
                    {'error': 'current_amount is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                current_amount = float(current_amount)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'current_amount must be a valid number'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if current_amount < 0:
                return Response(
                    {'error': 'Current amount cannot be negative'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if current_amount > goal.target_amount:
                return Response(
                    {'error': 'Current amount cannot exceed target amount'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            goal.current_amount = current_amount
            goal.save()
            
            serializer = self.get_serializer(goal)
            return Response(serializer.data)
        
        except FinancialGoal.DoesNotExist:
            return Response(
                {'error': 'Financial goal not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error updating goal: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    # Add queryset attribute to fix the basename issue
    queryset = Expense.objects.none()  # Dummy queryset
    
    @action(detail=False, methods=['post'])
    def monthly_trend(self, request):
        """Get monthly trend for expenses and income"""
        try:
            date_serializer = DateRangeSerializer(data=request.data)
            if not date_serializer.is_valid():
                return Response(date_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            start_date = date_serializer.validated_data['start_date']
            end_date = date_serializer.validated_data['end_date']
            
            # Generate monthly data
            current_date = start_date.replace(day=1)
            monthly_data = []
            
            while current_date <= end_date:
                # Calculate month end properly
                if current_date.month == 12:
                    next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    next_month = current_date.replace(month=current_date.month + 1, day=1)
                month_end = next_month - timedelta(days=1)
                
                # Ensure we don't go beyond the requested end_date
                if month_end > end_date:
                    month_end = end_date
                
                # Convert to timezone-aware datetimes
                month_start_tz = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
                month_end_tz = timezone.make_aware(datetime.combine(month_end, datetime.max.time()))
                
                # Get monthly expenses
                monthly_expenses_data = Expense.objects.filter(
                    user=request.user,
                    category__type='expense',
                    date__range=[month_start_tz, month_end_tz]
                ).aggregate(total=Sum('amount'))
                monthly_expenses = monthly_expenses_data['total'] or 0
                
                # Get monthly income
                monthly_income_data = Expense.objects.filter(
                    user=request.user,
                    category__type='income',
                    date__range=[month_start_tz, month_end_tz]
                ).aggregate(total=Sum('amount'))
                monthly_income = monthly_income_data['total'] or 0
                
                monthly_data.append({
                    'month': current_date.strftime('%b %Y'),
                    'expenses': monthly_expenses,
                    'income': monthly_income
                })
                
                # Move to next month
                current_date = next_month
            
            serializer = MonthlyTrendSerializer(monthly_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': f'Error generating monthly trend: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        try:
            today = timezone.now()
            start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Current month stats
            monthly_stats = Expense.objects.filter(
                user=request.user,
                date__gte=start_of_month
            ).aggregate(
                total_expenses=Sum('amount', filter=Q(category__type='expense')),
                total_income=Sum('amount', filter=Q(category__type='income'))
            )
            
            # Budget stats
            budget_stats = Budget.objects.filter(user=request.user).aggregate(
                total_budget=Sum('amount')
            )
            
            # Goal stats
            goal_stats = FinancialGoal.objects.filter(user=request.user).aggregate(
                total_target=Sum('target_amount'),
                total_current=Sum('current_amount')
            )
            
            stats = {
                'monthly_expenses': monthly_stats['total_expenses'] or 0,
                'monthly_income': monthly_stats['total_income'] or 0,
                'total_budget': budget_stats['total_budget'] or 0,
                'total_goals_target': goal_stats['total_target'] or 0,
                'total_goals_current': goal_stats['total_current'] or 0,
                'net_savings': (monthly_stats['total_income'] or 0) - (monthly_stats['total_expenses'] or 0)
            }
            
            return Response(stats)
        
        except Exception as e:
            return Response(
                {'error': f'Error generating dashboard stats: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )