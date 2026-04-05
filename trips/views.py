from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models, IntegrityError
from .models import Trip, Expense
from .serializers import TripSerializer, ExpenseSerializer

class TripListView(generics.ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Trip.objects.filter(traveller=self.request.user)
    
    def create(self, request, *args, **kwargs):
        print("=" * 50)
        print("Creating trip...")
        print(f"User: {request.user.username} (ID: {request.user.id})")
        print(f"User role: {request.user.role}")
        print(f"Request data: {request.data}")
        
        # Create a mutable copy of the data
        data = request.data.copy()
        
        # Ensure traveller is set
        if 'traveller' not in data or not data['traveller']:
            data['traveller'] = request.user.id
        
        print(f"Modified data: {data}")
        
        serializer = self.get_serializer(data=data)
        
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                print(f"Trip created successfully: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                print(f"IntegrityError: {e}")
                return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        serializer.save()

class TripDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TripSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'trip_id'
    
    def get_queryset(self):
        return Trip.objects.filter(traveller=self.request.user)

class ExpenseCreateView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def create(self, request, *args, **kwargs):
        trip_id = request.data.get('trip')
        try:
            trip = Trip.objects.get(trip_id=trip_id, traveller=request.user)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return super().create(request, *args, **kwargs)