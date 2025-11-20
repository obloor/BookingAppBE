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
    permission_classes = [IsAuthenticated]   # Must be logged in to access reservations

    # Users only see their own reservations
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(booked_by=self.request.user)
        return qs

    # Auto-assign the logged-in user
    def perform_create(self, serializer):
        serializer.save(
            booked_by=self.request.user,
            status='scheduled'         # default status
        )

    # POST
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        reservation.is_cancelled = True
        reservation.status = "cancelled"
        reservation.save(update_fields=["is_cancelled", "status"])

        return Response({"detail": "Cancelled"}, status=200)


