"""
URL configuration for budgetwise_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker.api_views import (
    CategoryViewSet, ExpenseViewSet, BudgetViewSet, 
    FinancialGoalViewSet, AnalyticsViewSet
)

# Create a router and register our viewsets with explicit basenames
router = DefaultRouter()
router.register(r'api/categories', CategoryViewSet, basename='category')
router.register(r'api/expenses', ExpenseViewSet, basename='expense')
router.register(r'api/budgets', BudgetViewSet, basename='budget')
router.register(r'api/goals', FinancialGoalViewSet, basename='financialgoal')
router.register(r'api/analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('tracker.urls')),  # This includes your tracker URLs
    path('', include(router.urls)),  # Include API routes
]

# Add API auth URLs
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]