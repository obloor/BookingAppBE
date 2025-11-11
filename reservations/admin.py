from django.contrib import admin
from .models import Room, Reservation  # Import both models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

# Register your models here.
admin.site.register(Room)
admin.site.register(Reservation)

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Group)