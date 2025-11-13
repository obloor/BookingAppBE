from rest_framework import serializers
from django.utils import timezone
from .models import Room, Reservation


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


from rest_framework import serializers
from django.utils import timezone
from .models import Room, Reservation

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class ReservationSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        source="room",
        write_only=True
    )
    booked_by_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = ("created_at", "is_cancelled", "status", "booked_by")

    def get_booked_by_username(self, obj):
        return obj.booked_by.username if obj.booked_by else None

    def create(self, validated_data):
        # Set the logged-in user as the booker
        validated_data['booked_by'] = self.context['request'].user
        validated_data['status'] = 'scheduled'  # Set initial status
        return super().create(validated_data)

    def validate(self, data):
        start = data.get("start_time")
        end = data.get("end_time")
        room = data.get("room")

        if start and end:
            if end <= start:
                raise serializers.ValidationError(
                    {"end_time": "End time must be after start time."}
                )

            if start <= timezone.now():
                raise serializers.ValidationError(
                    {"start_time": "Start time must be in the future."}
                )

            if room:
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
                        {"room": "This room is already booked for the selected time period."}
                    )

        return data