from rest_framework import generics, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Destination
from .serializers import DestinationSerializer, DestinationListSerializer

class DestinationListView(generics.ListAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationListSerializer  # Use list serializer for listing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['destination_type', 'is_popular']
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['average_rating', 'entry_fee', 'name']
    permission_classes = (permissions.AllowAny,)

class DestinationDetailView(generics.RetrieveAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer  # Use full serializer for detail
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'destination_id'

class DestinationCreateView(generics.CreateAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = (permissions.IsAdminUser,)

class DestinationUpdateView(generics.UpdateAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = (permissions.IsAdminUser,)
    lookup_field = 'destination_id'

class DestinationDeleteView(generics.DestroyAPIView):
    queryset = Destination.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    lookup_field = 'destination_id'