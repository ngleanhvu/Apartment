from datetime import datetime

from cloudinary.provisioning import users
from cloudinary.uploader import upload_image, upload
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apartmentapp import serializers
from apartmentapp.models import User, StorageLocker, Package, PackageStatus
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
        if user.is_staff:
            return StorageLocker.objects.filter(active=True)
        return StorageLocker.objects.filter(user=user, active=True)

class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = serializers.PackageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action=='change_status':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Package.objects.all()
        return Package.objects.filter(storage_locker__user=user)

    @action(methods=['POST'], detail=True)
    def change_status(self, request, pk=None):
        package=self.get_object()
        if package.status == PackageStatus.NOT_RECEIVED.value:
            package.status = PackageStatus.RECEIVED.value
            package.pickup_time=datetime.now()
            package.save()
            return Response({'message': 'Package status updated to RECEIVED.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Package is already RECEIVED.'}, status=status.HTTP_400_BAD_REQUEST)
