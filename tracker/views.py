from django.shortcuts import render
from rest_framework import viewsets
from .models import Expense
from .serializers import ExpenseSerializer
from django.contrib.auth.models import User # Required for a default user

# --- Views for Frontend/Templates ---
# Renders the main HTML frontend
def index(request):
    """
    Renders the main Expense Tracker frontend page.
    """
    return render(request, 'tracker/index.html')

# --- API ViewSet using DRF ---
class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Expenses to be viewed, created, or edited.
    It returns all expenses. (In a real app, this would be filtered by the user).
    """
    queryset = Expense.objects.all().order_by('-date', '-timestamp')
    serializer_class = ExpenseSerializer
    
    def perform_create(self, serializer):
        """
        Overrides the creation logic to ensure an expense is linked to a user.
        For simplicity, we'll assign it to the first user found (or a new one).
        """
        # NOTE: This is a placeholder for a real authentication system.
        # In a real app, you would use request.user if the user is logged in.
        try:
            # Try to get a default user (e.g., the first one created)
            default_user = User.objects.first()
            if not default_user:
                # Create a simple placeholder user if none exists
                default_user = User.objects.create_user(
                    username='placeholder_user', 
                    email='placeholder@example.com',
                    password=None
                )
        except Exception:
             # Handle database issues or other errors if needed
             default_user = None

        if default_user:
            serializer.save(user=default_user)
        else:
            # If no user can be set, raise an error or handle accordingly
            raise Exception("Could not assign an expense to a user.")
