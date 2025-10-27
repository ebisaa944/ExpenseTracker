from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Set up the router for the Expense API ViewSet, which handles CRUD operations
router = DefaultRouter()
router.register(r'expenses', views.ExpenseViewSet)

urlpatterns = [
    # 1. Main Root URL (for the frontend HTML page)
    # Accessible at: http://127.0.0.1:8000/
    path('', views.index, name='index'), 
    
    # 2. API Endpoints (for saving and retrieving data)
    # Accessible at: http://127.0.0.1:8000/api/expenses/
    path('api/', include(router.urls)),
]
