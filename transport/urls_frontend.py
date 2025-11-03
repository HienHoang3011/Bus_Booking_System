"""
Frontend URL configuration for bus booking
"""
from django.urls import path
from . import views_frontend

app_name = 'booking'

urlpatterns = [
    # Frontend booking pages
    path('trips/', views_frontend.trip_list, name='trip_list'),
    path('trip/<int:trip_id>/', views_frontend.trip_detail, name='trip_detail'),
    path('booking/create/<int:trip_id>/', views_frontend.booking_create, name='booking_create'),
    path('booking/<int:booking_id>/confirmation/', views_frontend.booking_confirmation, name='booking_confirmation'),
    path('my-bookings/', views_frontend.my_bookings, name='my_bookings'),
    # Admin pages
    path('manage/trips/', views_frontend.admin_trips, name='admin_trips'),
    # API endpoint for seat status
    path('api/trip/<int:trip_id>/seats/', views_frontend.get_trip_seats, name='get_trip_seats'),
]
