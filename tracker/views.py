from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, views as auth_views
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
import csv
import json
import io

# Make reportlab optional to avoid import errors
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from .models import Expense, Category, Budget, FinancialGoal, Income
from .forms import CustomUserCreationForm, ExpenseForm, BudgetForm, FinancialGoalForm, ExpenseFilterForm, IncomeForm, IncomeFilterForm

def index(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('tracker:dashboard')
    return render(request, 'tracker/index.html')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('tracker:dashboard')
    
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
                category = Category(
                    name=code,
                    user=user,
                    type=type,
                    color=color,
                    icon=icon
                )
                category.save()
            
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to ExpenseTracker.')
            return redirect('tracker:dashboard')
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
        
        monthly_income_data = Income.objects.filter(
            user=request.user,
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
        
        # Calculate savings
        monthly_savings = monthly_income - monthly_expenses
        savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
        
        context = {
            'monthly_expenses': monthly_expenses,
            'monthly_income': monthly_income,
            'monthly_savings': monthly_savings,
            'savings_rate': savings_rate,
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
            'monthly_savings': 0,
            'savings_rate': 0,
            'recent_expenses': [],
            'category_spending': [],
            'budget_alerts': [],
            'goals': [],
            'weekly_trend': [],
            'today': timezone.now(),
        })

# ===== INCOME VIEWS =====

@login_required
def income_list(request):
    """List all income with filtering and pagination"""
    try:
        incomes = Income.objects.filter(user=request.user).order_by('-date')
        
        # Initialize filter form
        filter_form = IncomeFilterForm(request.GET)
        
        # Apply filters
        if filter_form.is_valid():
            source = filter_form.cleaned_data.get('source')
            start_date = filter_form.cleaned_data.get('start_date')
            end_date = filter_form.cleaned_data.get('end_date')
            
            if source:
                incomes = incomes.filter(source=source)
            if start_date:
                incomes = incomes.filter(date__gte=timezone.make_aware(datetime.combine(start_date, datetime.min.time())))
            if end_date:
                incomes = incomes.filter(date__lte=timezone.make_aware(datetime.combine(end_date, datetime.max.time())))
        
        # Pagination
        paginator = Paginator(incomes, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Summary statistics
        total_data = incomes.aggregate(total=Sum('amount'))
        total_income = total_data['total'] or 0
        income_count = incomes.count()
        
        # Current month income
        current_month = timezone.now().month
        current_year = timezone.now().year
        monthly_income = Income.objects.filter(
            user=request.user,
            date__month=current_month,
            date__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        context = {
            'page_obj': page_obj,
            'filter_form': filter_form,
            'total_income': total_income,
            'income_count': income_count,
            'monthly_income': monthly_income,
            'current_month': timezone.now().strftime('%B %Y'),
        }
        return render(request, 'tracker/income_list.html', context)
    
    except Exception as e:
        messages.error(request, f"Error loading income: {str(e)}")
        return redirect('tracker:dashboard')

@login_required
def income_create(request):
    """Create new income"""
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Income added successfully!')
            return redirect('tracker:income_list')
    else:
        form = IncomeForm()
    
    return render(request, 'tracker/income_form.html', {
        'form': form,
        'title': 'Add New Income'
    })

@login_required
def income_edit(request, pk):
    """Edit existing income"""
    income = get_object_or_404(Income, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income updated successfully!')
            return redirect('tracker:income_list')
    else:
        form = IncomeForm(instance=income)
    
    return render(request, 'tracker/income_form.html', {
        'form': form,
        'title': 'Edit Income',
        'income': income
    })

@login_required
def income_delete(request, pk):
    """Delete income"""
    income = get_object_or_404(Income, pk=pk, user=request.user)
    
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Income deleted successfully!')
        return redirect('tracker:income_list')
    
    return render(request, 'tracker/income_confirm_delete.html', {'income': income})

@login_required
def income_summary(request):
    """Income summary view"""
    if not request.user.is_authenticated:
        return redirect('tracker:login')
    
    # Get time period from request or default to current month
    period = request.GET.get('period', 'month')
    now = timezone.now()
    
    if period == 'week':
        start_date = now - timedelta(days=now.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'year':
        start_date = datetime(now.year, 1, 1)
        end_date = datetime(now.year, 12, 31)
    else:  # month
        start_date = datetime(now.year, now.month, 1)
        end_date = datetime(now.year, now.month + 1, 1) - timedelta(days=1) if now.month < 12 else datetime(now.year, 12, 31)
    
    # Calculate income by source
    income_by_source = Income.objects.filter(
        user=request.user,
        date__date__gte=start_date,
        date__date__lte=end_date
    ).values('source').annotate(total=Sum('amount')).order_by('-total')
    
    # Calculate total income
    total_income = sum(item['total'] for item in income_by_source)
    
    # Recurring income stats
    recurring_income = Income.objects.filter(
        user=request.user,
        is_recurring=True
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Add income sources for display
    income_sources = Income.INCOME_SOURCES
    
    context = {
        'income_by_source': income_by_source,
        'total_income': total_income,
        'recurring_income': recurring_income,
        'income_sources': income_sources,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'tracker/income_summary.html', context)

# ===== EXPENSE VIEWS =====

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
        return redirect('tracker:dashboard')

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
            return redirect('tracker:expense_list')
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
            return redirect('tracker:expense_list')
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
        return redirect('tracker:expense_list')
    
    return render(request, 'tracker/expense_confirm_delete.html', {'expense': expense})

# ===== BUDGET VIEWS =====

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
        return redirect('tracker:dashboard')

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
            return redirect('tracker:budget_list')
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
            return redirect('tracker:budget_list')
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
        return redirect('tracker:budget_list')
    
    return render(request, 'tracker/budget_confirm_delete.html', {'budget': budget})

# ===== GOAL VIEWS =====

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
        return redirect('tracker:dashboard')

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
            return redirect('tracker:goal_list')
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
            return redirect('tracker:goal_list')
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
        return redirect('tracker:goal_list')
    
    return render(request, 'tracker/goal_confirm_delete.html', {'goal': goal})

# ===== EXPORT & REPORT VIEWS =====

@login_required
def export_expenses_csv(request):
    """Export expenses to CSV"""
    try:
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write headers
        writer.writerow(['Date', 'Description', 'Category', 'Amount', 'Payment Method', 'Notes'])
        
        # Write data
        expenses = Expense.objects.filter(user=request.user).select_related('category').order_by('-date')
        for expense in expenses:
            writer.writerow([
                expense.date.strftime('%Y-%m-%d'),
                expense.description,
                expense.category.get_name_display(),
                expense.amount,
                expense.get_payment_method_display(),
                expense.notes or ''
            ])
        
        return response
    
    except Exception as e:
        messages.error(request, f"Error exporting CSV: {str(e)}")
        return redirect('tracker:expense_list')

@login_required
def export_income_csv(request):
    """Export income to CSV"""
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="income.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Source', 'Description', 'Amount', 'Recurring', 'Notes'])
        
        incomes = Income.objects.filter(user=request.user).order_by('-date')
        for income in incomes:
            writer.writerow([
                income.date.strftime('%Y-%m-%d'),
                income.get_source_display(),
                income.description,
                income.amount,
                'Yes' if income.is_recurring else 'No',
                income.notes or ''
            ])
        
        return response
    
    except Exception as e:
        messages.error(request, f"Error exporting income CSV: {str(e)}")
        return redirect('tracker:income_list')

@login_required
def export_financial_report_pdf(request):
    """Export financial report to PDF"""
    if not REPORTLAB_AVAILABLE:
        messages.error(request, "PDF export is not available. Please install reportlab package.")
        return redirect('tracker:financial_reports')
    
    try:
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Add title
        title = Paragraph("Financial Report - ExpenseTracker", styles['Title'])
        elements.append(title)
        
        # Add date
        date_str = Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])
        elements.append(date_str)
        
        elements.append(Paragraph("<br/>", styles['Normal']))
        
        # Current month data
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Income data
        monthly_income = Income.objects.filter(
            user=request.user,
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Expense data
        monthly_expenses = Expense.objects.filter(
            user=request.user,
            category__type='expense',
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Summary table
        summary_data = [
            ['Category', 'Amount'],
            ['Total Income', f"${monthly_income:.2f}"],
            ['Total Expenses', f"${monthly_expenses:.2f}"],
            ['Net Savings', f"${monthly_income - monthly_expenses:.2f}"]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
        ]))
        elements.append(summary_table)
        
        elements.append(Paragraph("<br/>", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF value from buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="financial_report.pdf"'
        response.write(pdf)
        
        return response
    
    except Exception as e:
        messages.error(request, f"Error generating PDF report: {str(e)}")
        return redirect('tracker:dashboard')

@login_required
def financial_reports(request):
    """Financial reports dashboard"""
    # Get current month data for the reports page
    today = timezone.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_income = Income.objects.filter(
        user=request.user,
        date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        category__type='expense',
        date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_savings = monthly_income - monthly_expenses
    savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
    
    context = {
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_savings': monthly_savings,
        'savings_rate': savings_rate,
    }
    
    return render(request, 'tracker/financial_reports.html', context)

# ===== API VIEWS FOR CHARTS AND DATA =====

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
        
        monthly_income_data = Income.objects.filter(
            user=request.user,
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

# ===== PASSWORD RESET VIEWS =====

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'tracker/password_reset.html'
    email_template_name = 'tracker/password_reset_email.html'
    success_url = '/password-reset/done/'

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'tracker/password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'tracker/password_reset_confirm.html'
    success_url = '/password-reset/complete/'

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'tracker/password_reset_complete.html'

# ===== RECURRING TRANSACTIONS VIEW =====

@login_required
def process_recurring_transactions(request):
    """Process recurring transactions (to be called via cron job or manually)"""
    if not request.user.is_superuser and request.method != 'POST':
        messages.error(request, "Access denied.")
        return redirect('tracker:dashboard')
    
    try:
        today = timezone.now().date()
        processed_count = 0
        
        # Process recurring income
        recurring_incomes = Income.objects.filter(
            is_recurring=True,
            recurrence_pattern__in=['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']
        )
        
        for income in recurring_incomes:
            last_occurrence = income.date.date()
            should_create = False
            
            if income.recurrence_pattern == 'DAILY':
                should_create = (today - last_occurrence).days >= 1
            elif income.recurrence_pattern == 'WEEKLY':
                should_create = (today - last_occurrence).days >= 7
            elif income.recurrence_pattern == 'MONTHLY':
                should_create = today.month != last_occurrence.month or today.year != last_occurrence.year
            elif income.recurrence_pattern == 'YEARLY':
                should_create = today.year != last_occurrence.year
            
            if should_create:
                # Create new income record
                new_income = Income(
                    user=income.user,
                    amount=income.amount,
                    source=income.source,
                    description=f"Recurring: {income.description}",
                    date=timezone.now(),
                    is_recurring=True,
                    recurrence_pattern=income.recurrence_pattern,
                    notes=income.notes
                )
                new_income.save()
                processed_count += 1
        
        messages.success(request, f"Processed {processed_count} recurring transactions.")
        
    except Exception as e:
        messages.error(request, f"Error processing recurring transactions: {str(e)}")
    
    return redirect('tracker:dashboard')