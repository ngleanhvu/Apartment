from rest_framework import serializers
from apartmentapp.models import User, Fee, MonthlyFee, Room, Transaction, VehicleCard


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'username', 'changed_password', 'password', 'full_name', 'thumbnail', 'citizen_card', 'gender', 'is_active']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)  # hash password
        u.save()

        return u

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['value'] = instance.thumbnail.url if instance.thumbnail else ''

        return data

class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = ['id', 'name', 'description']

class MonthlyFeeSerializer(serializers.ModelSerializer):
    fee = FeeSerializer(read_only=True)
    class Meta:
        model = MonthlyFee
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'active']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class VehicleCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCard
        fields = '__all__'

