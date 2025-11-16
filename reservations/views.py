
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Room, Reservation
from .serializers import RoomSerializer, ReservationSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]
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
        serializer.save(booked_by=self.request.user, status='scheduled')

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        res = self.get_object()
        res.is_cancelled = True
        res.status = "cancelled"
        res.save(update_fields=["is_cancelled", "status"])
        return Response({"detail": "Cancelled"}, status=200)