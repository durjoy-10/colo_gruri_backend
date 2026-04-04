from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import (
    RegisterView, LoginView, UserProfileView, UserListView, 
    LogoutView, PendingGuidesView, VerifyGuideView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('pending-guides/', PendingGuidesView.as_view(), name='pending-guides'),
    path('verify-guide/<int:user_id>/', VerifyGuideView.as_view(), name='verify-guide'),
]