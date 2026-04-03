from rest_framework import generics, permissions
from .models import Trip, Expense
from .serializers import TripSerializer, ExpenseSerializer

class TripListView(generics.ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Trip.objects.filter(traveller=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(traveller=self.request.user)

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