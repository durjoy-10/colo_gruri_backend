from rest_framework import generics, permissions
from .models import Guide, GuideGroup
from .serializers import GuideSerializer, GuideGroupSerializer

class GuideGroupListView(generics.ListAPIView):
    queryset = GuideGroup.objects.filter(is_verified=True)
    serializer_class = GuideGroupSerializer
    permission_classes = (permissions.AllowAny,)

class GuideGroupDetailView(generics.RetrieveAPIView):
    queryset = GuideGroup.objects.all()
    serializer_class = GuideGroupSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'guide_group_id'

class GuideListView(generics.ListAPIView):
    queryset = Guide.objects.filter(is_active=True)
    serializer_class = GuideSerializer
    permission_classes = (permissions.AllowAny,)

class GuideDetailView(generics.RetrieveAPIView):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'guide_id'