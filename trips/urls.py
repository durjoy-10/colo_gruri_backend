from django.urls import path
from .views import TripListView, TripDetailView, ExpenseCreateView

urlpatterns = [
    path('', TripListView.as_view(), name='trip-list'),
    path('<int:trip_id>/', TripDetailView.as_view(), name='trip-detail'),
    path('add-expense/', ExpenseCreateView.as_view(), name='add-expense'),
]