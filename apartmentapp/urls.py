from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Ten API de so nhieu de theo chuan thiet ke RESTFull API
r = DefaultRouter()
r.register('users', views.UserViewSet, basename='users')
r.register('storagelockers', views.StorageLockerViewSet, 'storagelockers')


urlpatterns = [
    path('', include(r.urls))
]