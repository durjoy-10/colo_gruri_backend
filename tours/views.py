from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tour, TourImage, TourBooking
from .serializers import TourSerializer, TourCreateUpdateSerializer, TourImageSerializer, TourBookingSerializer
from decimal import Decimal


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
    serializer_class = TourSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'guide_group']
    search_fields = ['tour_name', 'description']
    ordering_fields = ['price_per_person', 'created_at']
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Tour.objects.filter(status='upcoming')
        
        if self.request.user.role == 'guide':
            from guides.models import Guide
            try:
                guide = Guide.objects.get(user=self.request.user)
                return Tour.objects.filter(guide_group=guide.guide_group)
            except Guide.DoesNotExist:
                return Tour.objects.none()
        
        if self.request.user.role == 'admin':
            return Tour.objects.all()
        
        return Tour.objects.filter(status='upcoming')


class TourDetailView(generics.RetrieveAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'tour_id'


class TourCreateView(generics.CreateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourCreateUpdateSerializer
    permission_classes = (IsGuideVerified,)
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        print("=" * 50)
        print("CREATE TOUR REQUEST")
        print(f"User: {request.user.username}, Role: {request.user.role}")
        
        if request.user.role == 'guide':
            from guides.models import Guide
            try:
                guide = Guide.objects.get(user=request.user)
                guide_group_id = guide.guide_group.guide_group_id
            except Guide.DoesNotExist:
                return Response(
                    {'error': 'Guide profile not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            guide_group_id = request.data.get('guide_group')
            if not guide_group_id:
                return Response(
                    {'error': 'guide_group is required for admin'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Extract data
        if hasattr(request.data, 'get'):
            tour_name = request.data.get('tour_name')
            description = request.data.get('description')
            total_seats = request.data.get('total_seats')
            price_per_person = request.data.get('price_per_person')
            discount_percentage = request.data.get('discount_percentage', 0)
            status_val = request.data.get('status', 'upcoming')
        else:
            tour_name = request.data.get('tour_name')
            description = request.data.get('description')
            total_seats = request.data.get('total_seats')
            price_per_person = request.data.get('price_per_person')
            discount_percentage = request.data.get('discount_percentage', 0)
            status_val = request.data.get('status', 'upcoming')
        
        # Validate
        errors = {}
        if not tour_name:
            errors['tour_name'] = 'This field is required'
        if not description:
            errors['description'] = 'This field is required'
        if not total_seats:
            errors['total_seats'] = 'This field is required'
        if not price_per_person:
            errors['price_per_person'] = 'This field is required'
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        from guides.models import GuideGroup
        try:
            guide_group = GuideGroup.objects.get(guide_group_id=guide_group_id)
        except GuideGroup.DoesNotExist:
            return Response(
                {'error': f'Guide group not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            tour = Tour.objects.create(
                tour_name=tour_name,
                description=description,
                guide_group=guide_group,
                total_seats=int(total_seats),
                available_seats=int(total_seats),
                price_per_person=float(price_per_person),
                discount_percentage=float(discount_percentage),
                status=status_val,
                total_expenses=0,
                is_locked=False
            )
            
            if 'cover_image' in request.FILES:
                tour.cover_image = request.FILES['cover_image']
                tour.save()
            
            serializer = TourSerializer(tour)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create tour: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TourUpdateView(generics.UpdateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourCreateUpdateSerializer
    permission_classes = (IsGuideVerified,)
    lookup_field = 'tour_id'
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    
    def update(self, request, *args, **kwargs):
        tour = self.get_object()
        print(f"Updating tour {tour.tour_id}")
        print(f"Request data: {request.data}")
        
        if tour.is_locked:
            return Response(
                {'error': 'This tour is completed and locked. Cannot edit.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.role == 'guide':
            from guides.models import Guide
            try:
                guide = Guide.objects.get(user=request.user)
                if tour.guide_group.guide_group_id != guide.guide_group.guide_group_id:
                    return Response(
                        {'error': 'You do not have permission to update this tour'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Guide.DoesNotExist:
                return Response(
                    {'error': 'Guide profile not found'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Update fields
        if 'tour_name' in request.data:
            tour.tour_name = request.data['tour_name']
        if 'description' in request.data:
            tour.description = request.data['description']
        if 'total_seats' in request.data:
            new_total = int(request.data['total_seats'])
            if new_total < (tour.total_seats - tour.available_seats):
                return Response(
                    {'error': f'Cannot reduce total seats below booked seats ({tour.total_seats - tour.available_seats})'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            tour.total_seats = new_total
        if 'price_per_person' in request.data:
            tour.price_per_person = float(request.data['price_per_person'])
        if 'discount_percentage' in request.data:
            tour.discount_percentage = float(request.data['discount_percentage'])
        if 'status' in request.data:
            old_status = tour.status
            tour.status = request.data['status']
            
            # If tour is being completed, auto-complete all confirmed bookings
            if request.data['status'] == 'completed' and old_status != 'completed':
                # Mark all confirmed bookings as completed
                TourBooking.objects.filter(tour=tour, status='confirmed').update(status='completed')
        
        if 'cover_image' in request.FILES:
            tour.cover_image = request.FILES['cover_image']
        
        tour.save()
        
        serializer = TourSerializer(tour)
        return Response(serializer.data)


class TourDeleteView(generics.DestroyAPIView):
    queryset = Tour.objects.all()
    permission_classes = (IsGuideVerified,)
    lookup_field = 'tour_id'
    
    def delete(self, request, *args, **kwargs):
        tour = self.get_object()
        print(f"Deleting tour {tour.tour_id}")
        
        if tour.is_locked:
            return Response(
                {'error': 'Completed tours cannot be deleted.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.role == 'guide':
            from guides.models import Guide
            try:
                guide = Guide.objects.get(user=request.user)
                if tour.guide_group.guide_group_id != guide.guide_group.guide_group_id:
                    return Response(
                        {'error': 'You do not have permission to delete this tour'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Guide.DoesNotExist:
                return Response(
                    {'error': 'Guide profile not found'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Delete the tour
        tour.delete()
        return Response({'message': 'Tour deleted successfully'}, status=status.HTTP_200_OK)


class TourCompleteView(APIView):
    permission_classes = (IsGuideVerified,)
    
    def post(self, request, tour_id):
        try:
            tour = Tour.objects.get(tour_id=tour_id)
            
            if request.user.role == 'guide':
                from guides.models import Guide
                try:
                    guide = Guide.objects.get(user=request.user)
                    if tour.guide_group.guide_group_id != guide.guide_group.guide_group_id:
                        return Response(
                            {'error': 'You do not have permission to complete this tour'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Guide.DoesNotExist:
                    return Response(
                        {'error': 'Guide profile not found'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            expenses = request.data.get('total_expenses', 0)
            
            tour.status = 'completed'
            tour.total_expenses = Decimal(str(expenses))
            tour.is_locked = True
            tour.save()
            
            # Auto-complete all confirmed bookings
            TourBooking.objects.filter(tour=tour, status='confirmed').update(status='completed')
            
            return Response({
                'message': 'Tour marked as completed',
                'total_revenue': float(tour.total_revenue),
                'total_expenses': float(tour.total_expenses),
                'net_profit': float(tour.net_profit)
            })
            
        except Tour.DoesNotExist:
            return Response({'error': 'Tour not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateBookingStatusView(APIView):
    permission_classes = (IsGuideVerified,)
    
    def patch(self, request, booking_id):
        try:
            booking = TourBooking.objects.get(booking_id=booking_id)
            tour = booking.tour
            
            if request.user.role == 'guide':
                from guides.models import Guide
                try:
                    guide = Guide.objects.get(user=request.user)
                    if tour.guide_group.guide_group_id != guide.guide_group.guide_group_id:
                        return Response(
                            {'error': 'You do not have permission to update this booking'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Guide.DoesNotExist:
                    return Response(
                        {'error': 'Guide profile not found'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            new_status = request.data.get('status')
            if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
                return Response(
                    {'error': 'Invalid status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prevent changing status of completed tours
            if tour.is_locked and new_status != 'completed':
                return Response(
                    {'error': 'Cannot change booking status for completed tours'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            booking.status = new_status
            booking.save()
            
            return Response({
                'message': f'Booking status updated to {new_status}',
                'booking': {
                    'id': booking.booking_id,
                    'status': booking.status,
                    'tour_name': booking.tour.tour_name,
                    'traveller_name': booking.traveller.get_full_name() or booking.traveller.username,
                    'total_amount': float(booking.total_amount)
                }
            })
            
        except TourBooking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)


class TourImageUploadView(generics.CreateAPIView):
    serializer_class = TourImageSerializer
    permission_classes = (IsGuideVerified,)
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        tour_id = request.POST.get('tour') or request.data.get('tour')
        
        if not tour_id:
            return Response({'error': 'tour ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tour = Tour.objects.get(tour_id=tour_id)
        except Tour.DoesNotExist:
            return Response({'error': 'Tour not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if tour.is_locked:
            return Response(
                {'error': 'Completed tours cannot be modified'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.role == 'guide':
            from guides.models import Guide
            try:
                guide = Guide.objects.get(user=request.user)
                if tour.guide_group.guide_group_id != guide.guide_group.guide_group_id:
                    return Response(
                        {'error': 'You do not have permission to add images'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Guide.DoesNotExist:
                return Response(
                    {'error': 'Guide profile not found'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if 'image' not in request.FILES:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)
        
        if image_file.size > 5 * 1024 * 1024:
            return Response({'error': 'File too large (max 5MB)'}, status=status.HTTP_400_BAD_REQUEST)
        
        is_primary = request.POST.get('is_primary', 'false').lower() == 'true'
        
        if is_primary:
            TourImage.objects.filter(tour=tour).update(is_primary=False)
        
        image = TourImage.objects.create(
            tour=tour,
            image=image_file,
            caption=request.POST.get('caption', ''),
            is_primary=is_primary,
            order=TourImage.objects.filter(tour=tour).count() + 1
        )
        
        serializer = TourImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TourImageDeleteView(generics.DestroyAPIView):
    queryset = TourImage.objects.all()
    permission_classes = (IsGuideVerified,)
    lookup_field = 'image_id'
    
    def delete(self, request, *args, **kwargs):
        image = self.get_object()
        tour = image.tour
        
        if tour.is_locked:
            return Response(
                {'error': 'Completed tours cannot be modified'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.role == 'guide':
            from guides.models import Guide
            try:
                guide = Guide.objects.get(user=request.user)
                if tour.guide_group.guide_group_id != guide.guide_group.guide_group_id:
                    return Response(
                        {'error': 'You do not have permission to delete this image'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Guide.DoesNotExist:
                return Response(
                    {'error': 'Guide profile not found'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        image.delete()
        return Response({'message': 'Image deleted successfully'}, status=status.HTTP_200_OK)


class TourImageSetPrimaryView(APIView):
    permission_classes = (IsGuideVerified,)
    
    def patch(self, request, image_id):
        try:
            image = TourImage.objects.get(image_id=image_id)
            tour = image.tour
            
            if tour.is_locked:
                return Response(
                    {'error': 'Completed tours cannot be modified'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if request.user.role == 'guide':
                from guides.models import Guide
                try:
                    guide = Guide.objects.get(user=request.user)
                    if tour.guide_group.guide_group_id != guide.guide_group.guide_group_id:
                        return Response(
                            {'error': 'You do not have permission'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Guide.DoesNotExist:
                    return Response(
                        {'error': 'Guide profile not found'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            TourImage.objects.filter(tour=tour).update(is_primary=False)
            image.is_primary = True
            image.save()
            
            return Response({'message': 'Primary image updated'})
        except TourImage.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)


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
        
        payment_method = data.get('payment_method')
        if payment_method in ['bkash', 'nagad', 'rocket']:
            payment_id = data.get('payment_id')
            if not payment_id:
                return Response(
                    {'error': f'{payment_method.upper()} transaction ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if len(payment_id) < 6:
                return Response(
                    {'error': 'Invalid transaction ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if payment_method == 'cash':
            guide_reference = data.get('guide_reference')
            if not guide_reference:
                return Response(
                    {'error': 'Guide reference is required for cash payment'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
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