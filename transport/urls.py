from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'routes', views.RouteViewSet, basename='route')
router.register(r'buses', views.BusViewSet, basename='bus')
router.register(r'seats', views.SeatViewSet, basename='seat')
router.register(r'trips', views.TripViewSet, basename='trip')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
