import base64
import hashlib
import hmac
import json
import uuid
import requests
import stripe
from cloudinary.uploader import upload_image, upload
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apartment import settings
from apartmentapp import serializers
from apartmentapp.models import User, MonthlyFee, Room, Transaction, MonthlyFeeStatus, PaymentGateway, TransactionStatus
from cloudinary.exceptions import Error as CloudinaryError

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
            user.changed_password = True
            user.save()

            return Response({'msg': 'Active user success!'},
                            status=status.HTTP_200_OK)

        except:
            return Response({'error', 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(active=True)
    serializers = serializers.RoomSerializer


class TransactionViewSet(viewsets.ViewSet,
                         generics.UpdateAPIView,
                         generics.RetrieveAPIView):
    queryset = Transaction.objects.filter(active=True)
    serializer_class = serializers.TransactionSerializer

    # Stripe payment
    @csrf_exempt
    @action(methods=['post'], detail=False, url_path='stripe', permission_classes=[IsAuthenticated])
    def create_checkout_session_stripe(self, request):
        try:

            monthly_fees = MonthlyFee.objects.filter(room=request.user.room, status=MonthlyFeeStatus.PENDING.value)

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
                                                     description=f"Phí dịch vụ của phòng {request.user.room}",
                                                     payment_gateway=PaymentGateway.STRIPE.value,
                                                     status=TransactionStatus.PENDING.value)

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=data,
                mode='payment',
                success_url='http://127.0.0.1:8000/success/',  # URL thành công
                cancel_url='http://127.0.0.1:8000/cancel/',  # URL hủy bỏ
                metadata={'transaction_id': transaction.id, 'user_id': request.user.id}
            )

            return Response({"sessionId": checkout_session.id}, status=status.HTTP_200_OK)
        except Exception as ex:
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
        print(transaction_id, user_id)
        transaction = Transaction.objects.filter(id=transaction_id).first()

        try:
            if event["type"] == "checkout.session.completed":
                user = User.objects.filter(id=user_id).first()

                (MonthlyFee.objects.filter(room=user.room, status=MonthlyFeeStatus.PENDING.value)
                 .update(status=MonthlyFeeStatus.PAID.value, transaction=transaction))

                transaction.status = TransactionStatus.SUCCESS.value
                transaction.save()
                return Response({'msg': 'Payment success'}, status=status.HTTP_200_OK)
        except Exception as ex:
            transaction.status = TransactionStatus.FAIL.value
            transaction.save()
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Momo
    @action(methods=['post'], detail=False, url_path='momo', permission_classes=[IsAuthenticated])
    def create_payment_momo(self, request):
        try:
            monthly_fees = MonthlyFee.objects.filter(room=request.user.room, status=MonthlyFeeStatus.PENDING.value)

            if not monthly_fees.exists():
                return Response({'msg': 'No monthly fee need to pay'})

            total_amount = sum(fee.amount for fee in monthly_fees)
            print(total_amount)

            import json
            import uuid
            import requests
            import hmac
            import hashlib

            # parameters send to MoMo get get payUrl
            endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
            accessKey = "F8BBA842ECF85"
            secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
            orderInfo = "pay with MoMo"
            partnerCode = "MOMO"
            redirectUrl = settings.MOMO_REDIRECT_URL
            ipnUrl = settings.MOMO_IPN_URL
            amount = str(int(total_amount))
            orderId = str(uuid.uuid4())
            requestId = str(uuid.uuid4())
            extraData = ""  # pass empty value or Encode base64 JsonString
            partnerName = "MoMo Payment"
            requestType = "payWithMethod"
            storeId = "Test Store"
            orderGroupId = ""
            autoCapture = True
            lang = "vi"
            orderGroupId = ""

            transaction = Transaction.objects.create(amount=total_amount,
                                                     user=request.user,
                                                     description=f"Phí dịch vụ của phòng {request.user.room}",
                                                     payment_gateway=PaymentGateway.MOMO.value,
                                                     status=TransactionStatus.PENDING.value)

            extra_data_str = f"transaction_id={transaction.id}"
            extraData = base64.b64encode(extra_data_str.encode('utf-8')).decode('utf-8')

            rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId \
                           + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl \
                           + "&requestId=" + requestId + "&requestType=" + requestType

            h = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'ascii'), hashlib.sha256)
            signature = h.hexdigest()

            print(signature)

            data = {
                'partnerCode': partnerCode,
                'orderId': orderId,
                'partnerName': partnerName,
                'ipnUrl': ipnUrl,
                'amount': amount,
                'requestType': requestType,
                'redirectUrl': redirectUrl,
                'orderInfo': orderInfo,
                'requestId': requestId,
                'extraData': extraData,
                'signature': signature,
                'accessKey': 'F8BBA842ECF85',
                'extractData': '',
                'lang': 'vi'
            }

            data = json.dumps(data)

            clen = len(data)
            response = requests.post(endpoint, data=data,
                                     headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

            print(response.json())
            return Response({"payUrl": response.json()['payUrl']}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @csrf_exempt
    @action(methods=['post'], detail=False,  url_path='webhook/momo')
    def momo_webhook(self, request):
        payload = request.body.decode('utf-8')
        print(payload)
        try:
            data = json.loads(payload)
            print(data)

            raw_signature = "&".join(
                [f"{key}={data[key]}" for key in sorted(data) if
                 key not in ["signature"]]
            )

            print(raw_signature)

            encoded_extra_data = data['extraData']
            print(encoded_extra_data)
            decoded_extra_data = base64.b64decode(encoded_extra_data).decode('utf-8')
            print(decoded_extra_data)

            # Tách các giá trị từ dữ liệu tùy chỉnh
            custom_data_map = dict(item.split("=") for item in decoded_extra_data.split("&"))

            # Lấy dữ liệu tùy chỉnh (ví dụ: userId, sessionId)
            transaction_id = int(custom_data_map.get('transaction_id'))
            print(transaction_id)

            # signature = hmac.new(
            #     settings.MOMO_SECRET_KEY.encode(),
            #     raw_signature.encode(),
            #     hashlib.sha256
            # ).hexdigest()

            # print(signature)
            # print(data["signature"])
            # if signature != data["signature"]:
            #     return Response({'error': 'Invalid Signature'}, status=status.HTTP_400_BAD_REQUEST)

            transaction = Transaction.objects.filter(id=transaction_id).first()
            print(transaction)
            try:
                if data["resultCode"] == 7002:
                    # Thanh toán thành công
                    user = transaction.user
                    transaction.status = TransactionStatus.SUCCESS.value
                    transaction.save()
                    MonthlyFee.objects.filter(room=user.room, status=MonthlyFeeStatus.PENDING.value).update(
                        status=MonthlyFeeStatus.PAID.value, transaction=transaction
                    )
                    return Response({'msg': 'Payment success'}, status=status.HTTP_200_OK)
            except Exception as ex:
                transaction.status = TransactionStatus.FAIL.value
                transaction.save()
                return Response({'error': 'Payment fail'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
