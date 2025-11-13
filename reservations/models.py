
from django.contrib.auth.models import User
from django.db import models

# Room Model
class Room(models.Model):
    # Room attributes
    name = models.CharField(max_length=80)
    number = models.PositiveIntegerField()
    location = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True, help_text="Is the room currently available for booking?")
    #equipment = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    # Orders rooms by name alphabetically
    class Meta:
        ordering = ["name"]

    # Returns room name
    def __str__(self):
        return self.name

# Reservation Model
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    # Reservation attributes
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="reservations")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    client = models.CharField(max_length=100)
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reservations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    attendees = models.PositiveIntegerField(default=1)

    # Orders reservations by start time in ascending order
    class Meta:
        ordering = ["start_time"]
        indexes = [models.Index(fields=["room", "start_time", "end_time"])]

    # Returns a summary of reservation data
    def __str__(self):
        return f"{self.client} in the {self.room.name} ({self.start_time} to {self.end_time})"
