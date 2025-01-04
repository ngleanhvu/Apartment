from django.conf import settings
from rest_framework import serializers
from apartmentapp.models import User, StorageLocker, Package, FeedbackResponse, Feedback
from twilio.rest import Client

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'password', 'full_name', 'thumbnail', 'citizen_card', 'gender']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password) # hash password
        u.save()

        return u

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['value'] = instance.thumbnail.url if instance.thumbnail else ''

        return data


class PackageSerializer(serializers.ModelSerializer):
    owner_phone = serializers.CharField(write_only=True)

    class Meta:
        model = Package
        fields = ['sender_name','recipient_name', 'owner_phone','quantity_items','thumbnail','description', 'status']

    def validate_owner_package_by_phone(self, value):
        try:
            user = User.objects.get(phone=value)
            if not hasattr(user, 'storage_locker'):
                raise serializers.ValidationError("Người nhận chưa được cấp storage locker")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Không tìm thấy người dùng với số điện thoại này")

    def create(self, validated_data):
        owner_phone=validated_data.pop('owner_phone')

        owner=User.objects.get(phone=owner_phone)
        storage_locker=owner.storage_locker
        package = Package.objects.create(
            **validated_data,
            storage_locker=storage_locker,
        )

        self.send_sms(package)
        return package

    def send_sms(self, package):
        # Khởi tạo Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        message = f"From {package.recipient_name}, your package is ready for pickup in your storage locker {package.storage_locker.number}."
        phone_number = f"+84{package.storage_locker.user.phone[1:]}" #Chuan so quoc te

        try:
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )

        except Exception as e:
            print(f"Error sending SMS: {e}")

class StorageLockerSerializer(serializers.ModelSerializer):
    packages = PackageSerializer(many=True)

    class Meta:
        model = StorageLocker
        fields = ['number', 'packages']


class FeedbackResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackResponse
        fields=['response']

class FeedbackSerializer(serializers.ModelSerializer):
    response=FeedbackResponseSerializer(required=False)

    class Meta:
        model=Feedback
        fields=['title','description','status', 'response']

