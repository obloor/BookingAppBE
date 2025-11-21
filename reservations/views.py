from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Room, Reservation
from .serializers import RoomSerializer, ReservationSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    # Rooms are public to view, admin-only to modify
    def get_permissions(self):
        # Anyone can view rooms
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]
        # Only admin can create/update/delete
        return [IsAdminUser()]


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("room", "booked_by").all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(booked_by=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            booked_by=self.request.user,
            status='scheduled'
        )

    @action(detail=False, methods=["get"], url_path="my")
    def my_reservations(self, request):
        qs = self.get_queryset().filter(booked_by=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
