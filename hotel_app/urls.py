from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomCategoryViewSet, RoomViewSet, BookingViewSet, check_room_availability

router = DefaultRouter()
router.register(r'categories', RoomCategoryViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("availability/", check_room_availability, name='room_availability'),
]