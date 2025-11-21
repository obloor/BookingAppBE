from rest_framework import serializers
from django.utils import timezone
from .models import Room, Reservation

# Room serializer
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

from rest_framework import serializers
from django.utils import timezone
from .models import Room, Reservation

# serializer for creating + updating reservations
class ReservationSerializer(serializers.ModelSerializer):
    # Writable room PK
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        required=False
    )

    room_details = RoomSerializer(source="room", read_only=True)

    booked_by_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
        # fields that should NOT be set by the frontend
        read_only_fields = ("created_at", "is_cancelled", "status", "booked_by")

    def get_booked_by_username(self, obj):
        return obj.booked_by.username if obj.booked_by else None

    # user + status check
    def create(self, validated_data):
        validated_data['booked_by'] = self.context['request'].user
        validated_data['status'] = 'scheduled'
        return super().create(validated_data)

    # main validation
def validate(self, data):
    room = data.get("room", getattr(self.instance, "room", None))
    start = data.get("start_time", getattr(self.instance, "start_time", None))
    end = data.get("end_time", getattr(self.instance, "end_time", None))

    if start and end:
        if end <= start:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )

        from django.utils import timezone
        if start <= timezone.now():
            raise serializers.ValidationError(
                {"start_time": "Start time must be in the future."}
            )

        # overlapping check
        overlapping = Reservation.objects.filter(
            room=room,
            is_cancelled=False,
            start_time__lt=end,
            end_time__gt=start
        )

        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError(
                {"room": "This room is already booked for that time."}
            )

    return data
