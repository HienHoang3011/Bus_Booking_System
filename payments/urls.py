from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'wallets', views.WalletViewSet, basename='wallet')

urlpatterns = [
    path('api/', include(router.urls)),
    # Frontend payment endpoints
    path('payment/<str:payment_id>/update-method/', views.update_payment_method, name='update_payment_method'),
]