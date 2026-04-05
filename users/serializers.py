from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'phone_number', 'national_id', 'profile_picture', 'address', 
                  'is_verified', 'date_joined', 'gender', 'date_of_birth', 'preferred_language')
        read_only_fields = ('id', 'date_joined', 'is_verified')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 
                  'last_name', 'role', 'phone_number', 'national_id', 'address',
                  'gender', 'date_of_birth', 'preferred_language')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if attrs.get('role') not in ['traveller', 'guide']:
            raise serializers.ValidationError({"role": "Role must be either 'traveller' or 'guide'"})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        
        if user.role == 'guide':
            user.is_verified = False
            user.save()
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'phone_number', 'national_id', 'profile_picture', 'address', 
                  'is_verified', 'date_joined', 'last_login', 'gender', 'date_of_birth', 'preferred_language')
        read_only_fields = ('id', 'date_joined', 'last_login', 'is_verified')