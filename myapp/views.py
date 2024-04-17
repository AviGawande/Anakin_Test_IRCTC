# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User, Train, Booking
from .serializers import UserSerializer, TrainSerializer, BookingSerializer

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_train(request):
    if request.method == 'POST':
        serializer = TrainSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_seat_availability(request):
    if request.method == 'GET':
        source = request.query_params.get('source')
        destination = request.query_params.get('destination')
        trains = Train.objects.filter(source=source, destination=destination)
        serializer = TrainSerializer(trains, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_seat(request):
    if request.method == 'POST':
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking_details(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = BookingSerializer(booking)
    return Response(serializer.data)
