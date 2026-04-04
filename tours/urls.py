from django.urls import path
from .views import (
    TourListView, TourDetailView, TourCreateView, TourUpdateView, TourDeleteView,
    BookingCreateView, MyBookingsView
)

urlpatterns = [
    path('', TourListView.as_view(), name='tour-list'),
    path('create/', TourCreateView.as_view(), name='tour-create'),
    path('<int:tour_id>/', TourDetailView.as_view(), name='tour-detail'),
    path('<int:tour_id>/update/', TourUpdateView.as_view(), name='tour-update'),
    path('<int:tour_id>/delete/', TourDeleteView.as_view(), name='tour-delete'),
    path('book/', BookingCreateView.as_view(), name='booking-create'),
    path('my-bookings/', MyBookingsView.as_view(), name='my-bookings'),
]