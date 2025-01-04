from os.path import basename

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import MonthlyFeeViewSet

# Ten API de so nhieu de theo chuan thiet ke RESTFull API
r = DefaultRouter()
r.register('users', views.UserViewSet, basename='users')
r.register('transactions', views.TransactionViewSet, basename='transactions')
r.register('vehicle-cards', views.VehicleCardViewSet, basename='vehicle-cards')
urlpatterns = [
    path('', include(r.urls)),
    path('monthly-fees/fees/<int:fee_id>/', MonthlyFeeViewSet.as_view({'get': 'list'}))
]
