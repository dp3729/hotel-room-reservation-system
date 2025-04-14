from rest_framework import serializers
from django.contrib.auth.models import User
from .models import RoomCategory, Room, Booking

class RoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCategory
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    category = RoomCategorySerializer(read_only=True)

    class Meta:
        model = Room
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'