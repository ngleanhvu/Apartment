from django.conf import settings
from rest_framework import serializers
from apartmentapp.models import User, StorageLocker, Package
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
    class Meta:
        model = Package
        fields = ['sender_name','recipient_name','status','pickup_time','quantity_items','thumbnail','storage_locker','description']

    def create(self, validated_data):
        package = super().create(validated_data)
        self.send_sms(package)
        return package

    def send_sms(self, package):
        # Khởi tạo Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        message = f"From {package.recipient_name}, your package is ready for pickup in your storage locker {package.storage_locker.number}."
        phone_number = f"+84{package.storage_locker.user.phone[1:]}" #Chuan so quoc te

        try:
            response=client.messages.create(
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

