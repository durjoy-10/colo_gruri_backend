from django.urls import path
from .views import (
    GuideGroupRegistrationView, GuideGroupListView, GuideGroupDetailView,
    PendingGuideGroupsView, VerifyGuideGroupView, RejectGuideGroupView
)

urlpatterns = [
    path('register-group/', GuideGroupRegistrationView.as_view(), name='register-group'),
    path('groups/', GuideGroupListView.as_view(), name='guide-group-list'),
    path('groups/<int:guide_group_id>/', GuideGroupDetailView.as_view(), name='guide-group-detail'),
    path('pending-groups/', PendingGuideGroupsView.as_view(), name='pending-groups'),
    path('verify-group/<int:group_id>/', VerifyGuideGroupView.as_view(), name='verify-group'),
    path('reject-group/<int:group_id>/', RejectGuideGroupView.as_view(), name='reject-group'),
]