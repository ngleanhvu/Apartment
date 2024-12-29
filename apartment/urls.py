import ckeditor_uploader
from django.urls import path, include, re_path

urlpatterns = [
    path('', include('apartmentapp.urls')),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
]
