from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import (
    CategoryViewSet, 
    ExpenseViewSet, 
    BudgetViewSet, 
    FinancialGoalViewSet,
    AnalyticsViewSet
)

app_name = 'tracker'

# Create router for API endpoints
router = DefaultRouter()
router.register(r'api/categories', CategoryViewSet, basename='category')
router.register(r'api/expenses', ExpenseViewSet, basename='expense')
router.register(r'api/budgets', BudgetViewSet, basename='budget')
router.register(r'api/goals', FinancialGoalViewSet, basename='financialgoal')
router.register(r'api/analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    # Public pages
    path('', views.index, name='index'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', 
         auth_views.LoginView.as_view(template_name='tracker/login.html'), 
         name='login'),
    path('logout/', 
         auth_views.LogoutView.as_view(template_name='tracker/logout.html'), 
         name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Settings & Profile URLs - NEWLY ADDED
    path('settings/', views.settings_overview, name='settings_overview'),
    path('settings/profile/', views.profile_settings, name='profile_settings'),
    path('settings/account/', views.account_settings, name='account_settings'),
    path('settings/application/', views.application_settings, name='application_settings'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/new/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Income - CORRECTED TO MATCH VIEWS
    path('income/', views.income_list, name='income_list'),
    path('income/new/', views.income_create, name='income_create'),
    path('income/<int:pk>/edit/', views.income_edit, name='income_edit'),
    path('income/<int:pk>/delete/', views.income_delete, name='income_delete'),
    path('income/summary/', views.income_summary, name='income_summary'),
    
    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/new/', views.budget_create, name='budget_create'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),
    
    # Financial Goals
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/new/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    
    # Reports & Export
    path('reports/', views.financial_reports, name='financial_reports'),
    path('reports/export/expenses/csv/', views.export_expenses_csv, name='export_expenses_csv'),
    path('reports/export/income/csv/', views.export_income_csv, name='export_income_csv'),
    path('reports/export/financial-report/pdf/', views.export_financial_report_pdf, name='export_financial_report_pdf'),
    
    # API endpoints for charts (regular views)
    path('api/expense-chart-data/', views.expense_chart_data, name='expense_chart_data'),
    path('api/category-chart-data/', views.category_chart_data, name='category_chart_data'),
    path('api/budget-progress-data/', views.budget_progress_data, name='budget_progress_data'),
    path('api/financial-summary/', views.financial_summary, name='financial_summary'),
    
    # Include API router URLs
    path('', include(router.urls)),
]

# Password Reset URLs (Custom Views)
urlpatterns += [
    path('password-reset/',
         views.CustomPasswordResetView.as_view(
             template_name='tracker/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         views.CustomPasswordResetDoneView.as_view(
             template_name='tracker/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         views.CustomPasswordResetConfirmView.as_view(
             template_name='tracker/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         views.CustomPasswordResetCompleteView.as_view(
             template_name='tracker/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]

# Additional URLs for new features
urlpatterns += [
    # Recurring Transactions
    path('recurring/process/', views.process_recurring_transactions, name='process_recurring_transactions'),
]