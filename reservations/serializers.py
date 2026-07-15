from django.db import transaction
from rest_framework import serializers
from django.utils import timezone
from .models import Room, Reservation


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class ReservationSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        required=False
    )
    room_details = RoomSerializer(source="room", read_only=True)
    booked_by_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = ("created_at", "is_cancelled", "status", "booked_by")

    def get_booked_by_username(self, obj):
        return obj.booked_by.username if obj.booked_by else None

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                {"detail": "Authentication required to create a reservation."}
            )

        validated_data["booked_by"] = user
        validated_data["status"] = "scheduled"

        room = validated_data["room"]
        start = validated_data["start_time"]
        end = validated_data["end_time"]

        with transaction.atomic():
            # Lock this room's active reservations until the transaction commits,
            # so a concurrent request has to wait its turn to check overlap.
            overlapping = Reservation.objects.select_for_update().filter(
                room=room,
                is_cancelled=False,
                start_time__lt=end,
                end_time__gt=start,
            )
            if overlapping.exists():
                raise serializers.ValidationError(
                    {"room": "This room is already booked for that time."}
                )
            return super().create(validated_data)

    def validate(self, data):
        room = data.get("room", getattr(self.instance, "room", None))
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        end = data.get("end_time", getattr(self.instance, "end_time", None))

        # Require room on create; on update, allow existing instance.room
        if not room:
            raise serializers.ValidationError(
                {"room": "Room is required."}
            )

        # Validate times only when both are present
        if start and end:
            if end <= start:
                raise serializers.ValidationError(
                    {"end_time": "End time must be after start time."}
                )

            if start <= timezone.now():
                raise serializers.ValidationError(
                    {"start_time": "Start time must be in the future."}
                )

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