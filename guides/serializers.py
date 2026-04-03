from rest_framework import serializers
from .models import Guide, GuideGroup, GuideGroupMember
from users.serializers import UserSerializer

class GuideSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Guide
        fields = '__all__'
        read_only_fields = ('guide_id', 'joined_date', 'rating', 'total_tours')

class GuideGroupSerializer(serializers.ModelSerializer):
    guides_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GuideGroup
        fields = '__all__'
        read_only_fields = ('guide_group_id', 'created_at')
    
    def get_guides_count(self, obj):
        return obj.guides.count()

class GuideGroupMemberSerializer(serializers.ModelSerializer):
    guide_details = GuideSerializer(source='guide', read_only=True)
    
    class Meta:
        model = GuideGroupMember
        fields = '__all__'