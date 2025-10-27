from django.urls import path
from . import views

# Set the app name for namespacing
app_name = 'tracker'

urlpatterns = [
    # path for the main dashboard/frontend page
    path('', views.index, name='index'), 
    
    # In a full project, you would add API paths here:
    # path('api/expenses/', views.ExpenseListCreate.as_view(), name='expense-list'),
    # path('api/expenses/<int:pk>/', views.ExpenseDetail.as_view(), name='expense-detail'),
]
