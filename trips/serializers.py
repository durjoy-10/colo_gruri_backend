from rest_framework import serializers
from django.db import models  # Add this import for models.Sum()
from .models import Trip, TripDestination, Expense
from destinations.serializers import DestinationSerializer

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('expense_id',)

class TripDestinationSerializer(serializers.ModelSerializer):
    destination_details = DestinationSerializer(source='destination', read_only=True)
    
    class Meta:
        model = TripDestination
        fields = '__all__'

class TripSerializer(serializers.ModelSerializer):
    destinations = TripDestinationSerializer(many=True, read_only=True)
    expenses = ExpenseSerializer(many=True, read_only=True)
    total_expenses = serializers.SerializerMethodField()
    
    class Meta:
        model = Trip
        fields = '__all__'  # Note: Use '__all__' not '_all_'
        read_only_fields = ('trip_id', 'created_at', 'updated_at')
    
    def get_total_expenses(self, obj):
        return obj.expenses.aggregate(total=models.Sum('amount'))['total'] or 0