from oauthlib.uri_validate import query

from apartmentapp.paginations import PackagePagination
from apartmentapp.serializers import StorageLockerSerializer, FeedbackSerializer, FeedbackResponseSerializer, \
    SurveySerializer, QuestionOptionSerializer, QuestionSerializer, MonthlyFeeSerializer, \
    FeeSerializer, ResponseSerializer, SurveyRetriveSerializer
from datetime import datetime
from threading import activeCount
from tkinter.ttk import Treeview
from cloudinary.provisioning import users
from cloudinary.uploader import upload_image, upload
from cloudinary.exceptions import Error as CloudinaryError
from django.db import transaction

from apartmentapp.models import StorageLocker, Package, PackageStatus, Feedback, FeedbackResponse, FeedbackStatus, \
    Survey, Question, QuestionOption, User, MonthlyFee, Room, Transaction, MonthlyFeeStatus, PaymentGateway, \
    TransactionStatus, Fee, VehicleCard, Relationship, Response
from rest_framework.views import APIView

from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response as RestResponse


from apartment import settings
from apartmentapp import serializers, paginations

from apartmentapp.permissions import MonthlyFeePerms



import stripe
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


# Create your views here.

# Request 1
class UserViewSet(viewsets.ViewSet,
                  generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer

    @action(methods=['get'], detail=False, url_path='current-user',  permission_classes = [IsAuthenticated])
    def current_user(self, request):
        return RestResponse(serializers.UserSerializer(request.user).data, status=status.HTTP_200_OK)

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
            return RestResponse({'error': 'Phone or password or thumbnail is required'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not password.__eq__(retype_password):
            return RestResponse({'error': 'Retype password is not correct'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            user = User.objects.filter(phone=username).first()

            if user.changed_password:
                return RestResponse({'msg': 'Người dùng đã kích hoạt tài khoản trước đó'},
                                status=status.HTTP_202_ACCEPTED)

            try:
                upload_result = upload(thumbnail)
                user.thumbnail = upload_result['secure_url']
            except CloudinaryError as ex:
                return RestResponse({'error': 'Upload thumbnail fail'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user.set_password(password)
            user.changed_password = True
            user.save()

            return RestResponse({'msg': 'Active user success!'},
                            status=status.HTTP_200_OK)

        except:
            return RestResponse({'error', 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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
                return RestResponse({'msg': 'No monthly fee need to pay'})

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
            return RestResponse({"clientSecret": payment_intent.client_secret}, status=status.HTTP_200_OK)

        except Exception as ex:
            print(ex)
            return RestResponse({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            return RestResponse({'error': 'Invalid Payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return RestResponse({'error': 'Invalid Signature'}, status=status.HTTP_400_BAD_REQUEST)

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
                return RestResponse({'msg': 'Payment success'}, status=status.HTTP_200_OK)
        except Exception as ex:
            transaction.status = TransactionStatus.FAIL.value
            transaction.save()
            print(ex)
            return RestResponse({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                return RestResponse({'msg': 'No monthly fee need to pay'})

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
                return RestResponse({'error': 'Upload thumbnail fail'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            monthly_fees.update(status=MonthlyFeeStatus.PAID.value, transaction=transaction)

            return RestResponse({"msg": 'Thanh toán thành công'}, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex)
            transaction.status = TransactionStatus.FAIL.value
            transaction.save()
            return RestResponse({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        return RestResponse(serializers.MonthlyFeeSerializer(queryset, many=True, context={'request': request}).data, status=status.HTTP_200_OK)

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

            return RestResponse({serializers.VehicleCardSerializer(v).data},
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            return RestResponse({'error': str(ex)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], detail=False, url_path='users')
    def get_by_user(self, request):
        try:

            user = request.user
            vehicle_cards = VehicleCard.objects.filter(user=user).all()

            return RestResponse({'vehicle_cards': serializers.VehicleCardSerializer(vehicle_cards, many=True).data},
                            status=status.HTTP_200_OK)

        except Exception as ex:
            return RestResponse({'error': str(ex)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FeeViewSet(viewsets.ViewSet,
                 generics.ListAPIView):
    queryset = Fee.objects.filter(active=True)
    serializer_class = FeeSerializer


class StorageLockerViewSet(viewsets.ViewSet, generics.ListAPIView):
    serializer_class = serializers.StorageLockerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return StorageLocker.objects.filter(active=True)
        return StorageLocker.objects.filter(user=user, active=True)


class PackageViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    serializer_class = serializers.PackageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = paginations.PackagePagination

    def get_permissions(self):
        if self.action=='list':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        query=Package.objects.filter(storage_locker__user=user)

        q=self.request.query_params.get('q')
        if q:
            query = query.filter(sender_name__icontains=q)

        return query


class FeedbackViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
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
            return RestResponse({"detail": "Feedback is RESOLVED"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save(
                admin=self.request.user,
                feedback=feedback
            )
            feedback.status = FeedbackStatus.RESOLVED.value
            feedback.save()
            return RestResponse(serializer.data)
        return RestResponse(serializer.errors)

# class FeedbackResponseViewSet(viewsets.ModelViewSet):
#     queryset = FeedbackResponse.objects.filter(active=True)
#     serializer_class = FeedbackResponseSerializer
#     permission_classes = [permissions.IsAdminUser]

#Survey
class SurveyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Survey.objects.filter(active=True, status='Published')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return SurveyRetriveSerializer
        return SurveySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'submit_response']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]


    @action(detail=True, methods=['POST'])
    def submit_response(self, request, pk=None):
        survey = self.get_object()

        if Response.objects.filter(survey=survey, resident=request.user).exists():
            return RestResponse(
                {"error": "You have already submitted a response to this survey"},
                status=status.HTTP_400_BAD_REQUEST
            )

        answers = request.data.get('answers', [])
        # Lưu câu trả lời cho mỗi câu hỏi
        for answer in answers:
            question_id = answer.get('question')
            option_id = answer.get('option')

            question = Question.objects.get(id=question_id)
            option = QuestionOption.objects.get(id=option_id)

                # Lưu câu trả lời vào Response
            Response.objects.create(
                resident=request.user,
                survey=survey,
                question=question,
                question_option=option
            )

        return RestResponse({'message': 'Survey responses submitted successfully.'}, status=status.HTTP_200_OK)

# class QuestionViewSet(viewsets.ModelViewSet):
#     queryset = Question.objects.filter(active=True)
#     serializer_class = QuestionSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_permissions(self):
#         if self.action=='list':
#             return [permissions.IsAuthenticated()]
#         return [permissions.IsAdminUser()]
#
# class QuestionOptionViewSet(viewsets.ModelViewSet):
#     queryset = QuestionOption.objects.filter(active=True)
#     serializer_class = QuestionOptionSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
# class AnswerViewSet(viewsets.ModelViewSet):
#     queryset = Answer.objects.filter(active=True)
#     serializer_class = AnswerSerializer
#     permissions=[permissions.IsAuthenticated]
#
#     def get_permissions(self):
#         if self.action == 'create':
#             return [permissions.IsAuthenticated()]
#         return [permissions.IsAdminUser()]
#
class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.filter(active=True)
    serializer_class = ResponseSerializer
    permissions=[permissions.IsAdminUser]


