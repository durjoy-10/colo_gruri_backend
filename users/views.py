from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, RegisterSerializer, UserProfileSerializer


# Custom permission for admin role
class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response(
                {'error': 'Invalid Credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if user.role == 'guide' and not user.is_verified:
            return Response(
                {'error': 'Your account is pending verification by admin. Please wait.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUserRole,)  # Use custom permission
    
    def get_queryset(self):
        return User.objects.all()


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        
        return Response({"message": "Successfully logged out."})


class PendingGuidesView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAdminUserRole,)
    
    def get_queryset(self):
        return User.objects.filter(role='guide', is_verified=False)


class VerifyGuideView(APIView):
    permission_classes = (IsAdminUserRole,)
    
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, role='guide')
            user.is_verified = True
            user.save()
            return Response({'message': 'Guide verified successfully'})
        except User.DoesNotExist:
            return Response({'error': 'Guide not found'}, status=status.HTTP_404_NOT_FOUND)