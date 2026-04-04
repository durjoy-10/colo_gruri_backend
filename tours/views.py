from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tour, TourBooking
from .serializers import TourSerializer, TourBookingSerializer


class IsGuideOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['guide', 'admin']


class IsGuideVerified(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or 
            (request.user.role == 'guide' and request.user.is_verified)
        )


class TourListView(generics.ListAPIView):
    queryset = Tour.objects.filter(status='upcoming')
    serializer_class = TourSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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
    permission_classes = (IsGuideVerified,)
    
    def create(self, request, *args, **kwargs):
        # If admin, allow creating tour without guide profile
        if request.user.role == 'admin':
            # Check if guide_group is provided in request
            guide_group_id = request.data.get('guide_group')
            if not guide_group_id:
                return Response(
                    {'error': 'guide_group is required for creating tour'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from guides.models import GuideGroup
            try:
                guide_group = GuideGroup.objects.get(guide_group_id=guide_group_id)
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(guide_group=guide_group)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except GuideGroup.DoesNotExist:
                return Response(
                    {'error': f'Guide group with id {guide_group_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # For guides, use their own group
        from guides.models import Guide
        try:
            guide = Guide.objects.get(user=request.user)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(guide_group=guide.guide_group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Guide.DoesNotExist:
            return Response(
                {'error': 'Guide profile not found. Please complete your guide profile first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        # This is handled in create method
        pass


class TourUpdateView(generics.UpdateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = (IsGuideVerified,)
    lookup_field = 'tour_id'


class TourDeleteView(generics.DestroyAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = (IsGuideVerified,)
    lookup_field = 'tour_id'


class BookingCreateView(generics.CreateAPIView):
    queryset = TourBooking.objects.all()
    serializer_class = TourBookingSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def create(self, request, *args, **kwargs):
        if request.user.role != 'traveller':
            return Response(
                {'error': 'Only travellers can book tours'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        data['traveller'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        tour = serializer.validated_data['tour']
        number_of_travellers = serializer.validated_data['number_of_travellers']
        
        if tour.available_seats < number_of_travellers:
            return Response(
                {'error': f'Only {tour.available_seats} seats available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tour.available_seats -= number_of_travellers
        tour.save()
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
    
    def perform_create(self, serializer):
        serializer.save()


class MyBookingsView(generics.ListAPIView):
    serializer_class = TourBookingSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'traveller':
            return TourBooking.objects.filter(traveller=user)
        elif user.role == 'guide':
            from guides.models import Guide
            try:
                guide = Guide.objects.get(user=user)
                return TourBooking.objects.filter(tour__guide_group=guide.guide_group)
            except Guide.DoesNotExist:
                return TourBooking.objects.none()
        
        return TourBooking.objects.none()