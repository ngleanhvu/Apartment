from rest_framework import serializers
from apartmentapp.models import User

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
