from django.contrib import admin
from .models import Category, Expense, Budget, FinancialGoal

admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Budget)
admin.site.register(FinancialGoal)

admin.site.site_header = "ExpenseTracker Administration"
admin.site.site_title = "ExpenseTracker Admin"