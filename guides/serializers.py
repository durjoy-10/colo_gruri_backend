from rest_framework import serializers
from .models import Guide, GuideGroup, GuideGroupMember
from users.models import User

class GuideGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideGroup
        fields = '__all__'
        read_only_fields = ('guide_group_id', 'created_at', 'is_verified')

class GuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        fields = '__all__'
        read_only_fields = ('guide_id', 'joined_date', 'rating', 'total_tours')

class GuideGroupMemberSerializer(serializers.ModelSerializer):
    guide_details = GuideSerializer(source='guide', read_only=True)
    
    class Meta:
        model = GuideGroupMember
        fields = '__all__'

class GuideGroupRegistrationSerializer(serializers.Serializer):
    # Group Information
    guide_groupname = serializers.CharField(max_length=100)
    group_email = serializers.EmailField()
    group_phone = serializers.CharField(max_length=17)
    group_address = serializers.CharField(required=False, allow_blank=True)
    group_description = serializers.CharField(required=False, allow_blank=True)
    guide_group_number = serializers.IntegerField(min_value=1, max_value=8)
    
    # Guide Members List
    guides = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=8
    )
    
    def validate_guides(self, value):
        # Check if number of guides matches guide_group_number
        if len(value) != self.initial_data.get('guide_group_number', len(value)):
            raise serializers.ValidationError("Number of guides doesn't match group size")
        
        # Check for duplicate usernames or emails within the group
        usernames = [g.get('username') for g in value]
        emails = [g.get('email') for g in value]
        
        if len(usernames) != len(set(usernames)):
            raise serializers.ValidationError("Duplicate usernames in guide group")
        
        if len(emails) != len(set(emails)):
            raise serializers.ValidationError("Duplicate emails in guide group")
        
        # Check if usernames or emails already exist in database
        for guide in value:
            if User.objects.filter(username=guide.get('username')).exists():
                raise serializers.ValidationError(f"Username '{guide.get('username')}' already exists")
            if User.objects.filter(email=guide.get('email')).exists():
                raise serializers.ValidationError(f"Email '{guide.get('email')}' already exists")
        
        return value
    
    def create(self, validated_data):
        # Create Guide Group
        guide_group = GuideGroup.objects.create(
            guide_groupname=validated_data['guide_groupname'],
            email=validated_data['group_email'],
            phone_number=validated_data['group_phone'],
            address=validated_data.get('group_address', ''),
            description=validated_data.get('group_description', ''),
            guide_group_number=validated_data['guide_group_number'],
            is_verified=False  # Pending verification
        )
        
        created_guides = []
        
        # Create each guide user and guide profile
        for idx, guide_data in enumerate(validated_data['guides']):
            # Create User account
            user = User.objects.create_user(
                username=guide_data['username'],
                email=guide_data['email'],
                password=guide_data['password'],
                first_name=guide_data.get('first_name', ''),
                last_name=guide_data.get('last_name', ''),
                role='guide',
                phone_number=guide_data.get('phone_number', ''),
                national_id=guide_data.get('national_id', ''),
                address=guide_data.get('address', ''),
                is_verified=False  # Pending verification
            )
            
            # Create Guide profile
            guide = Guide.objects.create(
                user=user,
                guide_group=guide_group,
                name=f"{guide_data.get('first_name', '')} {guide_data.get('last_name', '')}".strip(),
                username=guide_data['username'],
                email=guide_data['email'],
                national_id=guide_data.get('national_id', ''),
                phone_number=guide_data.get('phone_number', ''),
                gender=guide_data.get('gender', 'M'),
                experience_years=guide_data.get('experience_years', 0),
                languages_spoken=guide_data.get('languages_spoken', 'Bengali, English'),
                bio=guide_data.get('bio', '')
            )
            
            # Create group member
            GuideGroupMember.objects.create(
                guide_group=guide_group,
                guide=guide,
                index=idx + 1
            )
            
            created_guides.append(guide)
        
        return {
            'guide_group': guide_group,
            'guides': created_guides
        }