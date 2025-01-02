import stripe
from cloudinary.uploader import upload_image, upload
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apartment import settings
from apartmentapp import serializers
from apartmentapp.models import User, MonthlyFee, Room
from cloudinary.exceptions import Error as CloudinaryError
from apartmentapp.permissions import OwnerPerms, TransactionPerms

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
# Create your views here.

class UserViewSet(viewsets.ViewSet,
                  generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

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

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(active=True)
    serializers = serializers.RoomSerializer

class MonthlyFeeViewSet(viewsets.ViewSet,
                        generics.UpdateAPIView,
                        generics.RetrieveAPIView):
    queryset = MonthlyFee.objects.filter(active=True)
    serializer_class = serializers.MonthlyFeeSerializer

    # Stripe payment
    @action(methods=['put'], detail=True, url_path='stripe', permission_classes=[TransactionPerms])
    def create_checkout_session_stripe(self, request, pk):
        try:
            monthly_fee = self.get_object()
            self.check_object_permissions(request, monthly_fee) # goi de check xong roi moi
            amount = int(monthly_fee.amount)

            # Tao PaymentIntent
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'vnd',
                        'product_data': {
                            'name': monthly_fee.description,
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/success/',  # URL thành công
                cancel_url='http://127.0.0.1:8000/cancel/',  # URL hủy bỏ
            )

            return Response({"sessionId": checkout_session.id}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['put'], detail=True, url_path='momo')
    def create_check_out_session_momo(self, request, pk):
        pass


