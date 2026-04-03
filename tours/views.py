from rest_framework import generics, permissions, status, filters  # Add filters here
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tour, TourBooking
from .serializers import TourSerializer, TourBookingSerializer

class TourListView(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]  # Use filters.SearchFilter
    filterset_fields = ['status', 'guide_group']
    search_fields = ['tour_name', 'description']
    ordering_fields = ['price_per_person', 'created_at']

class TourDetailView(generics.RetrieveAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'tour_id'

class TourCreateView(generics.CreateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = (permissions.IsAdminUser,)

class BookingCreateView(generics.CreateAPIView):
    queryset = TourBooking.objects.all()
    serializer_class = TourBookingSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(traveller=self.request.user)

class MyBookingsView(generics.ListAPIView):
    serializer_class = TourBookingSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return TourBooking.objects.filter(traveller=self.request.user)