from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, ReservationViewSet
from .user_auth import RegisterView, CurrentUserView

router = DefaultRouter()
router.register(r"rooms", RoomViewSet, basename="room")
router.register("reservations", ReservationViewSet, basename="reservations")

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
] + router.urls
