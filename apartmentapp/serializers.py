from rest_framework import serializers
from apartmentapp.models import User, StorageLocker, Package


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
        fields = ['sender_name', 'recipient_name', 'status', 'pickup_time', 'quantity_items', 'thumbnail']

class StorageLockerSerializer(serializers.ModelSerializer):
    packages = PackageSerializer(many=True)

    class Meta:
        model = StorageLocker
        fields = ['number', 'packages']

