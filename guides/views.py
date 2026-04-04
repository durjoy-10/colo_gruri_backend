from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Guide, GuideGroup
from .serializers import GuideGroupSerializer, GuideSerializer, GuideGroupRegistrationSerializer

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