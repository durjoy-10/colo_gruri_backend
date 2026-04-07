from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from .models import Guide, GuideGroup, GuideGroupMember
from .serializers import GuideGroupSerializer, GuideSerializer, GuideGroupMemberSerializer, GuideGroupRegistrationSerializer
from tours.models import Tour, TourBooking
from django.db.models import Sum, Count, Q
from decimal import Decimal

class GuideDashboardView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        try:
            guide = Guide.objects.get(user=request.user)
            guide_group = guide.guide_group
            
            tours = Tour.objects.filter(guide_group=guide_group)
            
            # Get all bookings
            bookings = TourBooking.objects.filter(tour__in=tours)
            
            # Calculate revenue from CONFIRMED bookings only (not completed)
            confirmed_bookings = bookings.filter(status='confirmed')
            total_revenue = confirmed_bookings.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            # Calculate total expenses from completed tours
            total_expenses = tours.aggregate(total=Sum('total_expenses'))['total'] or Decimal('0.00')
            
            # Total profit = Revenue from confirmed bookings - Expenses
            total_profit = total_revenue - total_expenses
            
            # Statistics
            total_tours = tours.count()
            total_bookings = bookings.count()
            total_travellers = bookings.aggregate(total=Sum('number_of_travellers'))['total'] or 0
            
            upcoming_tours = tours.filter(status='upcoming').count()
            ongoing_tours = tours.filter(status='ongoing').count()
            completed_tours = tours.filter(status='completed').count()
            
            # Per-tour profit breakdown (only for tours with confirmed bookings)
            tour_profits = []
            for tour in tours:
                tour_confirmed_bookings = bookings.filter(tour=tour, status='confirmed')
                tour_revenue = tour_confirmed_bookings.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
                tour_profit = tour_revenue - tour.total_expenses
                
                tour_profits.append({
                    'tour_id': tour.tour_id,
                    'tour_name': tour.tour_name,
                    'revenue': float(tour_revenue),
                    'expenses': float(tour.total_expenses),
                    'profit': float(tour_profit),
                    'booking_count': tour_confirmed_bookings.count(),
                    'traveller_count': tour_confirmed_bookings.aggregate(total=Sum('number_of_travellers'))['total'] or 0,
                    'status': tour.status,
                    'is_locked': tour.is_locked,
                })
            
            # Recent bookings
            recent_bookings = bookings.select_related('tour', 'traveller').order_by('-booking_date')[:15]
            
            # Group members
            group_members = GuideGroupMember.objects.filter(guide_group=guide_group).select_related('guide')
            
            dashboard_data = {
                'guide_group': {
                    'id': guide_group.guide_group_id,
                    'name': guide_group.guide_groupname,
                    'member_count': guide_group.guide_group_number,
                    'is_verified': guide_group.is_verified,
                    'email': guide_group.email,
                    'phone': guide_group.phone_number,
                    'address': guide_group.address or 'Not provided',
                    'description': guide_group.description or 'No description',
                    'created_at': guide_group.created_at,
                },
                'guide_profile': {
                    'name': guide.name,
                    'username': guide.username,
                    'email': guide.email,
                    'phone': guide.phone_number,
                    'experience': guide.experience_years,
                    'languages': guide.languages_spoken,
                    'bio': guide.bio or 'No bio',
                    'rating': float(guide.rating),
                    'total_tours': guide.total_tours,
                },
                'statistics': {
                    'total_tours': total_tours,
                    'total_bookings': total_bookings,
                    'total_revenue': float(total_revenue),
                    'total_expenses': float(total_expenses),
                    'total_profit': float(total_profit),
                    'total_travellers': total_travellers,
                    'upcoming_tours': upcoming_tours,
                    'ongoing_tours': ongoing_tours,
                    'completed_tours': completed_tours,
                },
                'tour_profits': tour_profits,
                'recent_bookings': [
                    {
                        'id': booking.booking_id,
                        'tour_name': booking.tour.tour_name,
                        'tour_id': booking.tour.tour_id,
                        'traveller_name': booking.traveller.get_full_name() or booking.traveller.username,
                        'traveller_email': booking.traveller.email,
                        'traveller_phone': booking.traveller.phone_number,
                        'number_of_travellers': booking.number_of_travellers,
                        'total_amount': float(booking.total_amount),
                        'status': booking.status,
                        'booking_date': booking.booking_date,
                        'payment_method': booking.payment_method,
                        'payment_id': booking.payment_id,
                        'guide_reference': booking.guide_reference,
                        'special_requests': booking.special_requests,
                    }
                    for booking in recent_bookings
                ],
                'group_members': [
                    {
                        'id': member.guide.guide_id,
                        'name': member.guide.name,
                        'username': member.guide.username,
                        'email': member.guide.email,
                        'phone': member.guide.phone_number,
                        'experience': member.guide.experience_years,
                        'languages': member.guide.languages_spoken,
                        'rating': float(member.guide.rating),
                        'total_tours': member.guide.total_tours,
                        'joined_date': member.joined_at,
                    }
                    for member in group_members
                ],
            }
            
            return Response(dashboard_data)
            
        except Guide.DoesNotExist:
            return Response({'error': 'Guide profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GuideGroupBookingsView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        try:
            guide = Guide.objects.get(user=request.user)
            guide_group = guide.guide_group
            
            tours = Tour.objects.filter(guide_group=guide_group)
            bookings = TourBooking.objects.filter(tour__in=tours).order_by('-booking_date')
            
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            start = (page - 1) * page_size
            end = start + page_size
            
            total = bookings.count()
            
            booking_list = []
            for booking in bookings[start:end]:
                booking_list.append({
                    'id': booking.booking_id,
                    'tour_name': booking.tour.tour_name,
                    'tour_id': booking.tour.tour_id,
                    'traveller_name': booking.traveller.get_full_name() or booking.traveller.username,
                    'traveller_email': booking.traveller.email,
                    'traveller_phone': booking.traveller.phone_number,
                    'number_of_travellers': booking.number_of_travellers,
                    'total_amount': float(booking.total_amount),
                    'status': booking.status,
                    'booking_date': booking.booking_date,
                    'payment_method': booking.payment_method,
                    'payment_id': booking.payment_id,
                    'guide_reference': booking.guide_reference,
                    'special_requests': booking.special_requests,
                })
            
            return Response({
                'bookings': booking_list,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size if total > 0 else 1,
            })
            
        except Guide.DoesNotExist:
            return Response({'error': 'Guide profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ... rest of the views (GuideGroupRegistrationView, etc.) remain the same

class GuideGroupRegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = GuideGroupRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'message': 'Guide group registration successful! Please wait for admin verification.',
                'guide_group': GuideGroupSerializer(result['guide_group']).data,
                'guides': GuideSerializer(result['guides'], many=True).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuideGroupListView(generics.ListAPIView):
    queryset = GuideGroup.objects.filter(is_verified=True)
    serializer_class = GuideGroupSerializer
    permission_classes = (permissions.AllowAny,)


class GuideGroupDetailView(generics.RetrieveAPIView):
    queryset = GuideGroup.objects.all()
    serializer_class = GuideGroupSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'guide_group_id'


class PendingGuideGroupsView(generics.ListAPIView):
    serializer_class = GuideGroupSerializer
    permission_classes = (permissions.IsAdminUser,)
    
    def get_queryset(self):
        return GuideGroup.objects.filter(is_verified=False)


class VerifyGuideGroupView(APIView):
    permission_classes = (permissions.IsAdminUser,)
    
    def post(self, request, group_id):
        try:
            guide_group = GuideGroup.objects.get(guide_group_id=group_id)
            guide_group.is_verified = True
            guide_group.save()
            
            # Also verify all guides in the group
            guide_group.guides.all().update(is_active=True)
            for guide in guide_group.guides.all():
                guide.user.is_verified = True
                guide.user.save()
            
            return Response({'message': 'Guide group and all members verified successfully'})
        except GuideGroup.DoesNotExist:
            return Response({'error': 'Guide group not found'}, status=status.HTTP_404_NOT_FOUND)


class RejectGuideGroupView(APIView):
    permission_classes = (permissions.IsAdminUser,)
    
    def delete(self, request, group_id):
        try:
            guide_group = GuideGroup.objects.get(guide_group_id=group_id)
            # Delete all guides and users
            for guide in guide_group.guides.all():
                guide.user.delete()
                guide.delete()
            guide_group.delete()
            return Response({'message': 'Guide group rejected and deleted'})
        except GuideGroup.DoesNotExist:
            return Response({'error': 'Guide group not found'}, status=status.HTTP_404_NOT_FOUND)