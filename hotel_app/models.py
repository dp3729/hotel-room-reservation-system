from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class RoomCategory(models.Model):
    category_choices = [
        ('Deluxe Room', 'Deluxe Room'),
        ('Luxury Room', 'Luxury Room'),
        ('Luxury Suite', 'Luxury Suite'),
        ('Presidential Suite', 'Presidential Suite'),
    ]

    name = models.CharField(max_length=50, choices=category_choices, unique=True)
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name="rooms")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room_number} ({self.category.name})"
    
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} for Room {self.room.room_number}"