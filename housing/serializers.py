from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Property

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'user_type', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            user_type=validated_data.get('user_type', 'buyer')
        )
        return user

class PropertySerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.username')
    thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('owner', 'created_at')
        
    def get_thumbnail(self, obj):
        if obj.images.filter(is_thumbnail=True).exists():
            return obj.images.filter(is_thumbnail=True).first().image.url
        elif obj.images.exists():
            return obj.images.first().image.url
        elif obj.image:
            return obj.image.url
        return None
