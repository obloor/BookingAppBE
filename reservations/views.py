from django.utils.dateparse import parse_datetime
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
        # Anyone can view rooms; restrict writes later if you want
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
        room_id = self.request.query_params.get("room")
        start = self.request.query_params.get("from")
        end = self.request.query_params.get("to")
        if room_id:
            qs = qs.filter(room_id=room_id)
        if start and end:
            s, e = parse_datetime(start), parse_datetime(end)
            if s and e:
                qs = qs.filter(start_time__lt=e, end_time__gt=s)
        return qs.order_by("start_time")

    def perform_create(self, serializer):
        # this replaces your CBV form_valid() that set client/status, etc.
        res = serializer.save(booked_by=self.request.user, status="scheduled")
        # OPTIONAL: send email + schedule reminder (ported from your CBV):
        try:
            from django.template.loader import render_to_string
            from django.utils import timezone
            from .utils import send_email, schedule_reminder  # reuse your helpers

            context = {
                'user': self.request.user,
                'reservation': res,
                'time': timezone.localtime(res.start_time),
                'duration': (res.end_time - res.start_time).total_seconds() / 3600,
                'protocol': 'https',
                'domain': self.request.get_host(),
            }
            subject = f"Reservation Confirmed - {res.room.name}"
            html_content = render_to_string('conference/emails/reservation_confirmation.html', context)
            send_email(to_email=self.request.user.email, subject=subject, html_content=html_content)
            schedule_reminder(res)
        except Exception:
            pass  # don't break API if email fails

    def perform_destroy(self, instance):
        instance.is_cancelled = True
        instance.status = "cancelled"
        instance.save(update_fields=["is_cancelled", "status"])

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        # explicit cancel endpoint (alternative to DELETE)
        res = self.get_object()
        res.is_cancelled = True
        res.status = "cancelled"
        res.save(update_fields=["is_cancelled", "status"])
        return Response({"detail": "Cancelled"}, status=200)
