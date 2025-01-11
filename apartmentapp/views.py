
import stripe
from cloudinary.uploader import upload_image, upload
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from apartment import settings
from apartmentapp import serializers, paginations
from apartmentapp.models import User, MonthlyFee, Room, Transaction, MonthlyFeeStatus, PaymentGateway, \
    TransactionStatus, Fee, VehicleCard, Relationship
from cloudinary.exceptions import Error as CloudinaryError
from apartmentapp.permissions import MonthlyFeePerms, TransactionPerms
from apartmentapp.serializers import FeeSerializer
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


# Create your views here.

# Request 1
class UserViewSet(viewsets.ViewSet,
                  generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer

    @action(methods=['get'], detail=False, url_path='current-user',  permission_classes = [IsAuthenticated])
    def current_user(self, request):
        return Response(serializers.UserSerializer(request.user).data, status=status.HTTP_200_OK)

    # API active user
    @action(methods=['post'], detail=False, url_path='active-user')
    def active_user(self, request):
        # Lay du lieu tu request
        username = request.data.get('phone')
        password = request.data.get('password')
        retype_password = request.data.get('retype_password')
        thumbnail = request.FILES.get('avatar')

        print(username, password, retype_password, thumbnail)

        if not username or not password or not retype_password or not thumbnail:
            return Response({'error': 'Phone or password or thumbnail is required'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not password.__eq__(retype_password):
            return Response({'error': 'Retype password is not correct'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            user = User.objects.filter(phone=username).first()

            if user.changed_password:
                return Response({'msg': 'Người dùng đã kích hoạt tài khoản trước đó'},
                                status=status.HTTP_202_ACCEPTED)

            try:
                upload_result = upload(thumbnail)
                user.thumbnail = upload_result['secure_url']
            except CloudinaryError as ex:
                return Response({'error': 'Upload thumbnail fail'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user.set_password(password)
            user.changed_password = True
            user.save()

            return Response({'msg': 'Active user success!'},
                            status=status.HTTP_200_OK)

        except:
            return Response({'error', 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(active=True)
    serializers = serializers.RoomSerializer

# Request 2
class TransactionViewSet(viewsets.ViewSet,
                         generics.ListAPIView):

    queryset = Transaction.objects.filter(active=True)
    serializer_class = serializers.TransactionSerializer
    pagination_class = paginations.MonthlyFeePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        query = self.queryset
        query = query.filter(user=user, status=TransactionStatus.SUCCESS.value)
        fee_id = self.request.query_params.get('feeId')
        if fee_id:
            query= query.filter(monthly_fees__fee_id=fee_id)

        q = self.request.query_params.get("q")
        if q:
            query = query.filter(description__icontains=q)

        return query

    @action(methods=['get'], detail=True, url_path='detail', permission_classes=[TransactionPerms])
    def get_transaction_detail(self, request, pk):
        try:
            queryset = self.queryset.filter(id=pk)
            print(str(queryset.query))

            return Response(serializers.TransactionDetailSerializer(queryset.first()).data,
                            status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex)
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # Stripe payment
    @csrf_exempt
    @action(methods=['post'], detail=False, url_path='stripe', permission_classes=[IsAuthenticated])
    def create_checkout_session_stripe(self, request):
        try:
            ids = request.data.get('ids')
            ids = eval(ids)
            monthly_fees = MonthlyFee.objects.filter(
                room=request.user.room,
                status=MonthlyFeeStatus.PENDING.value,
                id__in = ids
            )


            if not monthly_fees.exists():
                return Response({'msg': 'No monthly fee need to pay'})

            monthly_fee = monthly_fees.first()

            data = []

            total_amount = sum(fee.amount for fee in monthly_fees)

            for item in monthly_fees:
                y = {
                    'price_data': {
                        'currency': 'vnd',
                        'product_data': {
                            'name': f"{item.fee.name} của phòng {item.room.room_number}",
                        },
                        'unit_amount': int(item.amount),
                    },
                    'quantity': 1,
                }

                data.append(y)

            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Chuyển đổi sang cent
                currency='vnd',
                metadata={'user_id': request.user.id,
                          'ids': ids,
                          'total_amount': total_amount,
                          "month": monthly_fee.created_date.month,
                          "year": monthly_fee.created_date.year},
                statement_descriptor_suffix="Amount"
            )

            # Trả về client_secret thay vì sessionId
            return Response({"clientSecret": payment_intent.client_secret}, status=status.HTTP_200_OK)

        except Exception as ex:
            print(ex)
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=False, url_path='webhook/stripe')
    def stripe_webhook(self, request):
        payload = request.body.decode(
            'utf-8')
        sig_header = request.headers.get("Stripe-Signature")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_TEST_ENDPOINT_SECRET
            )
        except ValueError as e:
            return Response({'error': 'Invalid Payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response({'error': 'Invalid Signature'}, status=status.HTTP_400_BAD_REQUEST)

        session = event["data"]["object"]
        total_amount = session["metadata"].get("total_amount")
        month = session["metadata"].get("month")
        year = session["metadata"].get("year")
        ids = session["metadata"].get("ids")
        print(event["type"])

        try:
            if event["type"] == "payment_intent.succeeded":

                transaction = Transaction.objects.create(amount=total_amount,
                                                         user=request.user,
                                                         description=f"Phí chung cư tháng {month} năm {year} phòng {request.user.room}",
                                                         payment_gateway=PaymentGateway.STRIPE.value,
                                                         status=TransactionStatus.SUCCESS.value)

                (MonthlyFee.objects.filter(room=request.user.room, status=MonthlyFeeStatus.PENDING.value, id__in=ids)
                 .update(status=MonthlyFeeStatus.PAID.value, transaction=transaction))

                return Response({'msg': 'Payment success'}, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex)
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Momo
    @action(methods=['post'], detail=False, url_path='momo', permission_classes=[IsAuthenticated])
    def create_payment_momo(self, request):
        try:
            ids = request.data.get('ids')
            ids = eval(ids)
            thumbnail = request.FILES.get('thumbnail')
            monthly_fees = MonthlyFee.objects.filter(
                room=request.user.room,
                status=MonthlyFeeStatus.PENDING.value,
                id__in=ids)

            if not monthly_fees.exists():
                return Response({'msg': 'No monthly fee need to pay'})

            monthly_fee = monthly_fees.first()

            total_amount = sum(fee.amount for fee in monthly_fees)

            transaction = Transaction(amount=total_amount,
                                                     user=request.user,
                                                     description=f"Phí chung cư tháng {monthly_fee.created_date.month} năm {monthly_fee.created_date.year} phòng {request.user.room}",
                                                     payment_gateway=PaymentGateway.MOMO.value,
                                                     status=TransactionStatus.SUCCESS.value)

            try:
                upload_result = upload(thumbnail)
                transaction.thumbnail = upload_result['secure_url']
            except CloudinaryError as ex:
                return Response({'error': 'Upload thumbnail fail'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            transaction.save()

            monthly_fees.update(status=MonthlyFeeStatus.PAID.value, transaction=transaction)

            return Response({"msg": 'Thanh toán thành công'}, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex)
            transaction.status = TransactionStatus.FAIL.value
            transaction.save()
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Request 3
class MonthlyFeeViewSet(ViewSet):

    permission_classes = [MonthlyFeePerms]
    pagination_class = paginations.MonthlyFeePagination

    @action(methods=['get'], detail=False, url_path='pending')
    def list_monthly_fee_pending(self, request):
        print('a')
        queryset = MonthlyFee.objects.filter(
            status=MonthlyFeeStatus.PENDING.value,
            active=True,
            room = request.user.room
        )

        print(queryset)

        return Response(serializers.MonthlyFeeSerializer(queryset, many=True, context={'request': request}).data, status=status.HTTP_200_OK)

# Request 4
class VehicleCardViewSet(viewsets.ViewSet,
                         generics.ListAPIView):
    model = VehicleCard
    serializer_class = serializers.VehicleCardSerializer
    queryset = VehicleCard.objects.filter(active=True)

    def get_permissions(self):
        if self.action.__eq__('list'):
            return [IsAdminUser(), IsAuthenticated()]

        return [IsAuthenticated()]


    @action(methods=['post'], detail=False, url_path='register')
    def register(self, request):
        try:
            user = request.user
            print(user)
            data = request.data
            print(data)
            full_name = data.get('full_name')
            citizen_card = data.get('citizen_card')
            vehicle_number = data.get('vehicle_number')

            v = VehicleCard(full_name=full_name,
                            citizen_card=citizen_card,
                            vehicle_number=vehicle_number,
                            user=user)

            if not user.citizen_card.__eq__(citizen_card):
                v.relationship = Relationship.RELATIVE.value

            v.save()

            return Response({serializers.VehicleCardSerializer(v).data},
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({'error': str(ex)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], detail=False, url_path='users')
    def get_by_user(self, request):
        try:

            user = request.user
            vehicle_cards = VehicleCard.objects.filter(user=user).all()

            return Response({'vehicle_cards': serializers.VehicleCardSerializer(vehicle_cards, many=True).data},
                            status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({'error': str(ex)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FeeViewSet(viewsets.ViewSet,
                 generics.ListAPIView):

    queryset = Fee.objects.filter(active=True)
    serializer_class = FeeSerializer

