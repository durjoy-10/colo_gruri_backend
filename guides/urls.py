from django.urls import path
from .views import GuideGroupListView, GuideGroupDetailView, GuideListView, GuideDetailView

urlpatterns = [
    path('groups/', GuideGroupListView.as_view(), name='guide-group-list'),
    path('groups/<int:guide_group_id>/', GuideGroupDetailView.as_view(), name='guide-group-detail'),
    path('', GuideListView.as_view(), name='guide-list'),
    path('<int:guide_id>/', GuideDetailView.as_view(), name='guide-detail'),
]