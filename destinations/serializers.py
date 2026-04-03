from rest_framework import serializers
from .models import Destination, DestinationImage, DestinationMap

class DestinationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DestinationImage
        fields = '__all__'

class DestinationMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = DestinationMap
        fields = '__all__'

class DestinationSerializer(serializers.ModelSerializer):
    images = DestinationImageSerializer(many=True, read_only=True)
    map_details = DestinationMapSerializer(source='map', read_only=True)
    
    class Meta:
        model = Destination
        fields = '__all__'
        read_only_fields = ('destination_id', 'created_at', 'updated_at', 'average_rating', 'total_reviews')

class DestinationListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Destination
        fields = ('destination_id', 'name', 'location', 'destination_type', 
                  'entry_fee', 'average_rating', 'is_popular', 'primary_image')
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return primary.image.url
        first_image = obj.images.first()
        if first_image:
            return first_image.image.url
        return None