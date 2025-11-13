from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Room, Reservation


# --- User Serializer for /api/users/me/ endpoint ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']


# --- Room Serializer ---
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


# serializers.py
class ReservationSerializer(serializers.ModelSerializer):
    booked_by_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
        # make only created_at and is_cancelled read-only now
        read_only_fields = ("created_at", "is_cancelled",)

    def get_booked_by_username(self, obj):
        return getattr(obj.booked_by, "username", None)

    def validate(self, data):
        if data["end_time"] <= data["start_time"]:
            raise serializers.ValidationError("End time must be greater than start time.")
        if data["start_time"] < timezone.now():
            raise serializers.ValidationError("Start time must be in the future.")

        # Prevent overlap
        existing_booking = Reservation.objects.filter(room=data["room"], is_cancelled=False)
        for booking in existing_booking:
            if data["start_time"] < booking.end_time and data["end_time"] > booking.start_time:
                raise serializers.ValidationError("This room is already booked for that period.")
        return data
