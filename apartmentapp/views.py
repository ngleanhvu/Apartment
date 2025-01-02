from cloudinary.provisioning import users
from cloudinary.uploader import upload_image, upload
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apartmentapp import serializers
from apartmentapp.models import User, StorageLocker, Package
from cloudinary.exceptions import Error as CloudinaryError

from apartmentapp.serializers import StorageLockerSerializer


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer

    # API active user
    @action(methods=['put'], detail=False, url_path='active-user')
    def active_user(self, request):
        # Lay du lieu tu request
        phone = request.data.get('phone')
        password = request.data.get('password')
        retype_password = request.data.get('retype_password')
        thumbnail = request.FILES.get('thumbnail')

        if not phone or not password or not retype_password or not thumbnail:
            return Response({'error': 'Phone or password or thumbnail is required'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not password.__eq__(retype_password):
            return Response({'error': 'Retype password is not correct'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            user = User.objects.filter(phone=phone).first()

            try:
                upload_result = upload(thumbnail)
                user.thumbnail = upload_result['secure_url']
            except CloudinaryError as ex:
                return Response({'error': 'Upload thumbnail fail'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user.set_password(password)
            user.changed_password=True
            user.save()
            return Response({'msg': 'Active user success!'},
                            status=status.HTTP_200_OK)
        except:
            return Response({'error', 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class StorageLockerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StorageLockerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        print("Logged-in user:", user)
        if user.is_staff:
            return StorageLocker.objects.filter(active=True)
        return StorageLocker.objects.filter(user=user, active=True)

class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = serializers.Package
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        user = self.request.user
        if user.is_staff:
            return Package.objects.all()
        return Package.objects.filter(storage_locker__user=user)
