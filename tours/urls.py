from django.urls import path
from .views import (
    TourListView, TourDetailView, TourCreateView, TourUpdateView, TourDeleteView,
    TourImageUploadView, TourImageDeleteView, TourImageSetPrimaryView,
    BookingCreateView, MyBookingsView, UpdateBookingStatusView, TourCompleteView
)

urlpatterns = [
    path('', TourListView.as_view(), name='tour-list'),
    path('create/', TourCreateView.as_view(), name='tour-create'),
    path('<int:tour_id>/', TourDetailView.as_view(), name='tour-detail'),
    path('<int:tour_id>/update/', TourUpdateView.as_view(), name='tour-update'),
    path('<int:tour_id>/delete/', TourDeleteView.as_view(), name='tour-delete'),
    path('<int:tour_id>/complete/', TourCompleteView.as_view(), name='tour-complete'),
    path('upload-image/', TourImageUploadView.as_view(), name='tour-upload-image'),
    path('delete-image/<int:image_id>/', TourImageDeleteView.as_view(), name='tour-delete-image'),
    path('images/<int:image_id>/set-primary/', TourImageSetPrimaryView.as_view(), name='tour-image-set-primary'),
    path('update-booking/<int:booking_id>/', UpdateBookingStatusView.as_view(), name='update-booking'),
    path('book/', BookingCreateView.as_view(), name='booking-create'),
    path('my-bookings/', MyBookingsView.as_view(), name='my-bookings'),
]