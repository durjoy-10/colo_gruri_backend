from django.urls import path
from .views import TourListView, TourDetailView, TourCreateView, BookingCreateView, MyBookingsView

urlpatterns = [
    path('', TourListView.as_view(), name='tour-list'),
    path('create/', TourCreateView.as_view(), name='tour-create'),
    path('<int:tour_id>/', TourDetailView.as_view(), name='tour-detail'),
    path('book/', BookingCreateView.as_view(), name='booking-create'),
    path('my-bookings/', MyBookingsView.as_view(), name='my-bookings'),
]