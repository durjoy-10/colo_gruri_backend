from django.urls import path
from .views import (
    DestinationListView, DestinationDetailView, DestinationCreateView,
    DestinationUpdateView, DestinationDeleteView
)

urlpatterns = [
    path('', DestinationListView.as_view(), name='destination-list'),
    path('create/', DestinationCreateView.as_view(), name='destination-create'),
    path('<int:destination_id>/', DestinationDetailView.as_view(), name='destination-detail'),
    path('<int:destination_id>/update/', DestinationUpdateView.as_view(), name='destination-update'),
    path('<int:destination_id>/delete/', DestinationDeleteView.as_view(), name='destination-delete'),
]