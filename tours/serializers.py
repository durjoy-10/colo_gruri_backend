from rest_framework import serializers
from .models import Tour, TourDestination, FoodPlan, TourBooking
from destinations.serializers import DestinationSerializer
from guides.serializers import GuideGroupSerializer
from users.serializers import UserSerializer

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
    guide_group_details = GuideGroupSerializer(source='guide_group', read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Tour
        fields = '__all__'
        read_only_fields = ('tour_id', 'created_at', 'updated_at')

class TourBookingSerializer(serializers.ModelSerializer):
    tour_details = TourSerializer(source='tour', read_only=True)
    traveller_details = UserSerializer(source='traveller', read_only=True)
    
    class Meta:
        model = TourBooking
        fields = '__all__'
        read_only_fields = ('booking_id', 'booking_date')