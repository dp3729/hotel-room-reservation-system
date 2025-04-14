from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from datetime import date, datetime
from rest_framework import viewsets, filters, permissions
from .models import RoomCategory, Room, Booking
from .serializers import RoomCategorySerializer, RoomSerializer, BookingSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

def home(request):
    rooms = get_available_rooms()
    return render(request, 'home.html', {'rooms': rooms})
    # return render(request, 'home.html')

class RoomCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RoomCategory.objects.all()
    serializer_class = RoomCategorySerializer

class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['room_number', 'category__name']

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# User Registration
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            login(request, user)
            messages.success(request, "Registration Successful!")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged In Successfully!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect('home')

# To show rooms
def room_list(request):
    rooms = Room.objects.select_related('category').all()
    return render(request, 'rooms.html', {'rooms': rooms})

def get_available_rooms():
    today = date.today()
    # To get all rooms that are not booked from today onwards
    booked_rooms = Room.objects.filter(bookings__check_out__gte=today).distinct()
    available_rooms = Room.objects.exclude(id__in=booked_rooms.values_list('id', flat=True))
    return available_rooms

@login_required
def book_room_view(request):
    rooms = Room.objects.all()

    if request.method == 'POST':
        room_id = request.POST.get('room')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        # Convert string date to Python datetime object
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

        # Check for overlap: does this room already have a booking in this date range?
        existing_bookings = Booking.objects.filter(
            room_id=room_id,
            check_in__lt=check_out_date,
            check_out__gt=check_in_date
        )

        if existing_bookings.exists():
            messages.error(request, 'This room is already booked for the selected dates.')
        else:
            Booking.objects.create(
                user=request.user,
                room_id=room_id,
                check_in=check_in_date,
                check_out=check_out_date
            )
            messages.success(request, 'Room Booked Successfully!')
            return redirect('home')  # You can redirect to a success page

    return render(request, 'book_room.html', {'rooms': rooms})

@api_view(['GET'])
def check_room_availability(request):
    room_category = request.GET.get('category')  # RoomCategory ID or Name
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if not room_category or not check_in or not check_out:
        return Response({"error": "Missing required parameters: category, check_in, check_out"}, status=400)

    # Convert to datetime
    try:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    # Get all rooms of this category
    rooms = Room.objects.filter(category__name=room_category)

    # Filter out rooms that are already booked in that date range
    unavailable_rooms = Booking.objects.filter(
        room__in=rooms,
        check_in__lt=check_out_date,
        check_out__gt=check_in_date
    ).values_list('room_id', flat=True)

    available_rooms = rooms.exclude(id__in=unavailable_rooms)

    serializer = RoomSerializer(available_rooms, many=True)
    return Response(serializer.data)

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-check_in')
    return render(request, 'my_bookings.html', {'bookings': bookings})