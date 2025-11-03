from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Expense, Category, Budget, FinancialGoal
from .forms import CustomUserCreationForm, ExpenseForm, BudgetForm, FinancialGoalForm, ExpenseFilterForm

def index(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tracker/index.html')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create default categories for the new user
            default_categories = [
                ('FOOD', 'Food & Dining', 'expense', '#FF6B6B', 'restaurant'),
                ('TRANSPORT', 'Transportation', 'expense', '#4ECDC4', 'directions_car'),
                ('UTILITIES', 'Utilities', 'expense', '#45B7D1', 'flash_on'),
                ('ENTERTAINMENT', 'Entertainment', 'expense', '#96CEB4', 'movie'),
                ('SHOPPING', 'Shopping', 'expense', '#FFEAA7', 'shopping_cart'),
                ('HEALTHCARE', 'Healthcare', 'expense', '#DDA0DD', 'local_hospital'),
                ('INCOME', 'Income', 'income', '#98D8C8', 'attach_money'),
            ]
            
            for code, display_name, type, color, icon in default_categories:
                Category.objects.create(
                    name=code,
                    user=user,
                    type=type,
                    color=color,
                    icon=icon
                )
            
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to ExpenseTracker.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'tracker/register.html', {'form': form})

@login_required
def dashboard(request):
    """Main dashboard view"""
    try:
        # Current month calculations
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Monthly expenses and income
        monthly_expenses_data = Expense.objects.filter(
            user=request.user,
            category__type='expense',
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))
        monthly_expenses = monthly_expenses_data['total'] or 0
        
        monthly_income_data = Expense.objects.filter(
            user=request.user,
            category__type='income',
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))
        monthly_income = monthly_income_data['total'] or 0
        
        # Recent expenses
        recent_expenses = Expense.objects.filter(user=request.user).select_related('category').order_by('-date')[:5]
        
        # Category-wise spending
        category_spending = Expense.objects.filter(
            user=request.user,
            category__type='expense',
            date__gte=start_of_month
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Budget alerts
        budget_alerts = []
        budgets = Budget.objects.filter(user=request.user).select_related('category')
        for budget in budgets:
            spent = budget.spent_amount()
            if spent > budget.amount * 0.8:  # Alert if spent more than 80% of budget
                budget_alerts.append({
                    'budget': budget,
                    'spent': spent,
                    'percentage': budget.progress_percentage()
                })
        
        # Financial goals
        goals = FinancialGoal.objects.filter(user=request.user)
        
        # Weekly spending trend
        weekly_trend = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            daily_total_data = Expense.objects.filter(
                user=request.user,
                category__type='expense',
                date__range=[day_start, day_end]
            ).aggregate(total=Sum('amount'))
            daily_total = daily_total_data['total'] or 0
            
            weekly_trend.append({
                'day': day.strftime('%a'),
                'amount': float(daily_total)
            })
        
        context = {
            'monthly_expenses': monthly_expenses,
            'monthly_income': monthly_income,
            'recent_expenses': recent_expenses,
            'category_spending': category_spending,
            'budget_alerts': budget_alerts,
            'goals': goals,
            'weekly_trend': weekly_trend,
            'today': today,
        }
        return render(request, 'tracker/dashboard.html', context)
    
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return render(request, 'tracker/dashboard.html', {
            'monthly_expenses': 0,
            'monthly_income': 0,
            'recent_expenses': [],
            'category_spending': [],
            'budget_alerts': [],
            'goals': [],
            'weekly_trend': [],
            'today': timezone.now(),
        })

@login_required
def expense_list(request):
    """List all expenses with filtering and pagination"""
    try:
        expenses = Expense.objects.filter(user=request.user).select_related('category').order_by('-date')
        
        # Initialize filter form
        filter_form = ExpenseFilterForm(request.GET, user=request.user)
        
        # Apply filters
        if filter_form.is_valid():
            category = filter_form.cleaned_data.get('category')
            start_date = filter_form.cleaned_data.get('start_date')
            end_date = filter_form.cleaned_data.get('end_date')
            payment_method = filter_form.cleaned_data.get('payment_method')
            
            if category:
                expenses = expenses.filter(category=category)
            if start_date:
                expenses = expenses.filter(date__gte=timezone.make_aware(datetime.combine(start_date, datetime.min.time())))
            if end_date:
                expenses = expenses.filter(date__lte=timezone.make_aware(datetime.combine(end_date, datetime.max.time())))
            if payment_method:
                expenses = expenses.filter(payment_method=payment_method)
        
        # Pagination
        paginator = Paginator(expenses, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Summary statistics
        total_data = expenses.aggregate(total=Sum('amount'))
        total_expenses = total_data['total'] or 0
        expense_count = expenses.count()
        
        context = {
            'page_obj': page_obj,
            'filter_form': filter_form,
            'total_expenses': total_expenses,
            'expense_count': expense_count,
        }
        return render(request, 'tracker/expense_list.html', context)
    
    except Exception as e:
        messages.error(request, f"Error loading expenses: {str(e)}")
        return redirect('dashboard')

@login_required
def expense_create(request):
    """Create new expense"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    
    return render(request, 'tracker/expense_form.html', {
        'form': form,
        'title': 'Add New Expense'
    })

@login_required
def expense_edit(request, pk):
    """Edit existing expense"""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    
    return render(request, 'tracker/expense_form.html', {
        'form': form,
        'title': 'Edit Expense',
        'expense': expense
    })

@login_required
def expense_delete(request, pk):
    """Delete expense"""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')
    
    return render(request, 'tracker/expense_confirm_delete.html', {'expense': expense})

@login_required
def budget_list(request):
    """List all budgets"""
    try:
        budgets = Budget.objects.filter(user=request.user).select_related('category')
        categories = Category.objects.filter(user=request.user, type='expense')
        
        # Calculate budget statistics
        budget_stats = []
        for budget in budgets:
            spent = budget.spent_amount()
            remaining = budget.remaining_amount()
            percentage = budget.progress_percentage()
            
            budget_stats.append({
                'budget': budget,
                'spent': spent,
                'remaining': remaining,
                'percentage': percentage
            })
        
        context = {
            'budget_stats': budget_stats,
            'categories': categories,
        }
        return render(request, 'tracker/budget_list.html', context)
    
    except Exception as e:
        messages.error(request, f"Error loading budgets: {str(e)}")
        return redirect('dashboard')

@login_required
def budget_create(request):
    """Create new budget"""
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)
    
    return render(request, 'tracker/budget_form.html', {
        'form': form,
        'title': 'Create Budget'
    })

@login_required
def budget_edit(request, pk):
    """Edit existing budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    
    return render(request, 'tracker/budget_form.html', {
        'form': form,
        'title': 'Edit Budget',
        'budget': budget
    })

@login_required
def budget_delete(request, pk):
    """Delete budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('budget_list')
    
    return render(request, 'tracker/budget_confirm_delete.html', {'budget': budget})

@login_required
def goal_list(request):
    """List all financial goals"""
    try:
        goals = FinancialGoal.objects.filter(user=request.user)
        
        context = {
            'goals': goals,
        }
        return render(request, 'tracker/goal_list.html', context)
    
    except Exception as e:
        messages.error(request, f"Error loading goals: {str(e)}")
        return redirect('dashboard')

@login_required
def goal_create(request):
    """Create new financial goal"""
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Financial goal created successfully!')
            return redirect('goal_list')
    else:
        form = FinancialGoalForm()
    
    return render(request, 'tracker/goal_form.html', {
        'form': form,
        'title': 'Create Financial Goal'
    })

@login_required
def goal_edit(request, pk):
    """Edit existing financial goal"""
    goal = get_object_or_404(FinancialGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Financial goal updated successfully!')
            return redirect('goal_list')
    else:
        form = FinancialGoalForm(instance=goal)
    
    return render(request, 'tracker/goal_form.html', {
        'form': form,
        'title': 'Edit Financial Goal',
        'goal': goal
    })

@login_required
def goal_delete(request, pk):
    """Delete financial goal"""
    goal = get_object_or_404(FinancialGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Financial goal deleted successfully!')
        return redirect('goal_list')
    
    return render(request, 'tracker/goal_confirm_delete.html', {'goal': goal})

# API Views for Charts and Data
@login_required
def expense_chart_data(request):
    """API endpoint for expense chart data"""
    try:
        # Last 6 months spending data
        data = []
        today = timezone.now()
        
        for i in range(5, -1, -1):
            month_start = today.replace(day=1) - timedelta(days=30*i)
            next_month = month_start + timedelta(days=32)
            month_end = next_month.replace(day=1) - timedelta(days=1)
            
            total_data = Expense.objects.filter(
                user=request.user,
                category__type='expense',
                date__range=[month_start, month_end]
            ).aggregate(total=Sum('amount'))
            total = total_data['total'] or 0
            
            data.append({
                'month': month_start.strftime('%b %Y'),
                'amount': float(total)
            })
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def category_chart_data(request):
    """API endpoint for category chart data"""
    try:
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        data = Expense.objects.filter(
            user=request.user,
            category__type='expense',
            date__gte=start_of_month
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        chart_data = {
            'labels': [item['category__name'] for item in data],
            'data': [float(item['total']) for item in data],
            'colors': [item['category__color'] for item in data],
        }
        
        return JsonResponse(chart_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def budget_progress_data(request):
    """API endpoint for budget progress data"""
    try:
        budgets = Budget.objects.filter(user=request.user).select_related('category')
        
        data = []
        for budget in budgets:
            spent = budget.spent_amount()
            data.append({
                'category': budget.category.get_name_display(),
                'budget': float(budget.amount),
                'spent': float(spent),
                'remaining': float(budget.remaining_amount()),
                'percentage': budget.progress_percentage()
            })
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def financial_summary(request):
    """API endpoint for financial summary"""
    try:
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Monthly totals
        monthly_expenses_data = Expense.objects.filter(
            user=request.user,
            category__type='expense',
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))
        monthly_expenses = monthly_expenses_data['total'] or 0
        
        monthly_income_data = Expense.objects.filter(
            user=request.user,
            category__type='income',
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))
        monthly_income = monthly_income_data['total'] or 0
        
        # Budget summary
        total_budget_data = Budget.objects.filter(user=request.user).aggregate(total=Sum('amount'))
        total_budget = total_budget_data['total'] or 0
        
        total_spent = sum(budget.spent_amount() for budget in Budget.objects.filter(user=request.user))
        
        summary = {
            'monthly_expenses': float(monthly_expenses),
            'monthly_income': float(monthly_income),
            'total_budget': float(total_budget),
            'total_spent': float(total_spent),
            'savings': float(monthly_income - monthly_expenses),
        }
        
        return JsonResponse(summary)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)