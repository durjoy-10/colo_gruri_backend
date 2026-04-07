from rest_framework import serializers
from .models import Tour, TourImage, TourDestination, FoodPlan, TourBooking
from destinations.serializers import DestinationSerializer
from guides.serializers import GuideGroupSerializer

class TourImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TourImage
        fields = ('image_id', 'image', 'image_url', 'caption', 'is_primary', 'order')
    
    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class FoodPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodPlan
        fields = '__all__'


class TourDestinationSerializer(serializers.ModelSerializer):
    destination_details = DestinationSerializer(source='destination', read_only=True)
    food_plans = FoodPlanSerializer(many=True, read_only=True)
    
    class Meta:
        model = TourDestination
        fields = '__all__'


class TourSerializer(serializers.ModelSerializer):
    destinations = TourDestinationSerializer(many=True, read_only=True)
    images = TourImageSerializer(many=True, read_only=True)
    guide_group_details = GuideGroupSerializer(source='guide_group', read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Tour
        fields = '__all__'
        read_only_fields = ('tour_id', 'created_at', 'updated_at', 'available_seats')
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        # Return first image if no cover image
        first_image = obj.images.filter(is_primary=True).first()
        if first_image:
            return first_image.image.url
        first_image = obj.images.first()
        return first_image.image.url if first_image else None


class TourCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ('tour_name', 'guide_group', 'description', 'total_seats', 
                  'price_per_person', 'discount_percentage', 'status', 'cover_image')
    
    def create(self, validated_data):
        # Set available_seats equal to total_seats
        validated_data['available_seats'] = validated_data['total_seats']
        return super().create(validated_data)


class TourBookingSerializer(serializers.ModelSerializer):
    tour_details = TourSerializer(source='tour', read_only=True)
    traveller_details = serializers.SerializerMethodField()
    
    class Meta:
        model = TourBooking
        fields = '__all__'
        read_only_fields = ('booking_id', 'booking_date')
        extra_kwargs = {
            'payment_id': {'required': False, 'allow_blank': True},
            'guide_reference': {'required': False, 'allow_blank': True},
        }
    
    def get_traveller_details(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.traveller).data