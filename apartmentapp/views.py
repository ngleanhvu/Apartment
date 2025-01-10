from datetime import datetime
from threading import activeCount
from tkinter.ttk import Treeview

from cloudinary.provisioning import users

import stripe
from cloudinary.uploader import upload_image, upload
from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response as RestResponse
from urllib3 import request

from apartmentapp import serializers
from apartmentapp.models import User, StorageLocker, Package, PackageStatus, Feedback, FeedbackResponse, FeedbackStatus, \
    Survey, Question, QuestionOption, Answer, Response, QuestionTypeEnum
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
from apartmentapp.permissions import MonthlyFeePerms
from apartmentapp.serializers import MonthlyFeeSerializer, FeeSerializer

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


from apartmentapp.serializers import StorageLockerSerializer, FeedbackSerializer, FeedbackResponseSerializer, \
    SurveySerializer, QuestionOptionSerializer, AnswerSerializer, ResponseSerializer, SurveyRetrieveSerializer, \
    ResponseCreateSerializer, QuestionSerializer


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
        query = query.filter(user=user, status=TransactionStatus.SUCCESS)
        fee_id = self.request.query_params.get('fee_id')
        if fee_id:
            query= query.filter(monthlyfee__fee_id=fee_id)

        q = self.request.query_params.get("q")
        if q:
            query = query.filter(description__icontains=q)

        return query


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

            transaction = Transaction.objects.create(amount=total_amount,
                                                     user=request.user,
                                                     description=f"Phí chung cư hằng tháng của phòng {request.user.room}",
                                                     payment_gateway=PaymentGateway.STRIPE.value,
                                                     status=TransactionStatus.PENDING.value)

            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Chuyển đổi sang cent
                currency='vnd',
                metadata={'transaction_id': transaction.id, 'user_id': request.user.id, 'ids': ids},
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
        transaction_id = session["metadata"].get("transaction_id")
        user_id = session["metadata"].get("user_id")
        ids = session["metadata"].get("ids")
        print(transaction_id, user_id, ids)
        transaction = Transaction.objects.filter(id=transaction_id).first()
        print(transaction)
        print(event["type"])
        try:
            if event["type"] == "payment_intent.succeeded":
                user = User.objects.filter(id=user_id).first()
                print(user)
                (MonthlyFee.objects.filter(room=user.room, status=MonthlyFeeStatus.PENDING.value, id__in=ids)
                 .update(status=MonthlyFeeStatus.PAID.value, transaction=transaction))

                transaction.status = TransactionStatus.SUCCESS.value
                transaction.save()
                return Response({'msg': 'Payment success'}, status=status.HTTP_200_OK)
        except Exception as ex:
            transaction.status = TransactionStatus.FAIL.value
            transaction.save()
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

            total_amount = sum(fee.amount for fee in monthly_fees)

            transaction = Transaction(amount=total_amount,
                                                     user=request.user,
                                                     description=f"Phí dịch vụ của phòng {request.user.room}",
                                                     payment_gateway=PaymentGateway.MOMO.value,
                                                     status=TransactionStatus.SUCCESS.value)

            transaction.save()

            try:
                upload_result = upload(thumbnail)
                transaction.thumbnail = upload_result['secure_url']
            except CloudinaryError as ex:
                transaction.status = TransactionStatus.FAIL.value
                transaction.save()
                return Response({'error': 'Upload thumbnail fail'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        if self.action=='list':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Package.objects.all()
        return Package.objects.filter(storage_locker__user=user)

    @action(methods=['POST'], detail=True, permission_classes=[permissions.IsAdminUser])
    def change_status(self, request, pk=None):
        package=self.get_object()
        if package.status == PackageStatus.NOT_RECEIVED.value:
            package.status = PackageStatus.RECEIVED.value
            package.pickup_time=datetime.now()
            package.save()
            return Response({'message': 'Package status updated to RECEIVED.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Package is already RECEIVED.'}, status=status.HTTP_400_BAD_REQUEST)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.filter(active=True)
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user=self.request.user
        if user.is_staff:
            return Feedback.objects.filter(active=True)
        return Feedback.objects.filter(resident=user, active=True)

    def perform_create(self, serializer):
        serializer.save(resident=self.request.user)

    @action(methods=['POST'], detail=True, permission_classes=[IsAdminUser])
    def respond(self, request, pk=None):
        feedback=self.get_object()
        serializer=FeedbackResponseSerializer(data=request.data)
        if feedback.status == FeedbackStatus.RESOLVED.value:
            return Response({"detail": "Feedback is RESOLVED"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save(
                admin=self.request.user,
                feedback=feedback
            )
            feedback.status = FeedbackStatus.RESOLVED.value
            feedback.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    queryset = Fee.objects.filter(active=True)
    serializer_class = FeeSerializer
class FeedbackResponseViewSet(viewsets.ModelViewSet):
    queryset = FeedbackResponse.objects.filter(active=True)
    serializer_class = FeedbackResponseSerializer
    permission_classes = [permissions.IsAdminUser]

#Survey
class SurveyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SurveySerializer
        return SurveyRetrieveSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'submit_response']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Survey.objects.filter(active=True)
        return Survey.objects.filter(active=True, status='Published')


    @action(detail=True, methods=['POST'])
    def submit_response(self, request, pk=None):
        survey = self.get_object()

        if Response.objects.filter(survey=survey, resident=request.user).exists():
            return RestResponse(
                {"error": "You have already submitted a response to this survey"},
                status=status.HTTP_400_BAD_REQUEST
            )

        request_data = request.data.copy()
        request_data['survey'] = survey.id

        serializer = ResponseCreateSerializer(data=request_data)
        if not serializer.is_valid():
            return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response = serializer.save(resident=request.user)

        return RestResponse(
            ResponseSerializer(response).data,
            status=status.HTTP_201_CREATED
        )

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.filter(active=True)
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action=='list':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class QuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = QuestionOption.objects.filter(active=True)
    serializer_class = QuestionOptionSerializer
    permission_classes = [permissions.IsAuthenticated]

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.filter(active=True)
    serializer_class = AnswerSerializer
    permissions=[permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.filter(active=True)
    serializer_class = ResponseSerializer
    permissions=[permissions.IsAdminUser]


