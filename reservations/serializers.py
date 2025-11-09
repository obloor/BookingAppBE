from rest_framework import serializers
from django.utils import timezone
from .models import Room, Reservation


def get_booked_by_username(self, obj):
    return getattr(obj.booked_by, "username", None)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

class ReservationSerializer(serializers.ModelSerializer):
    booked_by_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = ("booked_by", "created_at", "is_cancelled",)


    # Validation for end time > start time and start time > current time
    def validate(self, data):
        if data["end_time"] <= data["start_time"]:
            raise serializers.ValidationError("End time must be greater than start time.")
        if data["start_time"] < timezone.now():
            raise serializers.ValidationError("Start time must be in the future.")

        existing_booking = Reservation.objects.filter(room=data["room"], is_cancelled=False)

        # Prevents double bookings
        for booking in existing_booking:
            if data["start_time"] < booking.end_time and data["end_time"] > booking.start_time:
                raise serializers.ValidationError("This room is already booked for that period.")

        return data