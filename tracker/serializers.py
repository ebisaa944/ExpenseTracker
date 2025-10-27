from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer to convert Expense model instances to JSON and vice-versa.
    """
    # Define a read-only field for the category display name
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Expense
        # We include 'category_display' here so it is returned in the API response
        fields = ['id', 'user', 'title', 'amount', 'category', 'date', 'timestamp', 'category_display']
        read_only_fields = ['user', 'timestamp'] # User will be set by the view
