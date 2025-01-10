from django.conf import settings
from rest_framework import serializers
from apartmentapp.models import User, StorageLocker, Package, FeedbackResponse, Feedback, Survey, Question, \
    QuestionOption, Answer, Response
from twilio.rest import Client
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

#Storage Locker
class PackageSerializer(serializers.ModelSerializer):
    owner_phone = serializers.CharField(write_only=True)

    class Meta:
        model = Package
        fields = ['id', 'sender_name','recipient_name', 'owner_phone','quantity_items','thumbnail','description', 'status']

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
        fields = ['id','number', 'packages']

#Feedback
class FeedbackResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackResponse
        fields=['id', 'response']

class FeedbackSerializer(serializers.ModelSerializer):
    response=FeedbackResponseSerializer(required=False)

    class Meta:
        model=Feedback
        fields=['id', 'title','description','status', 'response']

#Survey
class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'content']

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id','title', 'description', 'start_date', 'end_date', 'status']

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id','content', 'type', 'survey', 'options']

class SurveyRetrieveSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ['id','title', 'description', 'start_date', 'end_date', 'status', 'questions']


class AnswerSerializer(serializers.ModelSerializer):
    selected_options = QuestionOptionSerializer(many=True, read_only=True)
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'question', 'text_answer', 'boolean_answer', 'selected_options']

class AnswerCreateSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=QuestionOption.objects.all(),
        required=False
    )

    class Meta:
        model = Answer
        fields = ['question', 'text_answer', 'boolean_answer', 'selected_options']

    def validate(self, data):
        question = data.get('question')

        if question.type == 'Single choice':
            selected_options = data.get('selected_options', [])
            if len(selected_options) != 1:
                raise serializers.ValidationError(
                    f"Question {question.id} requires only 1 option to be selected."
                )

        return data

class ResponseSerializer(serializers.ModelSerializer):
    answers=AnswerSerializer(many=True, required=True)

    class Meta:
        model=Response
        fields = ['id', 'survey', 'resident', 'submitted_at', 'answers']
        ordering=['-submitted_at']


class ResponseCreateSerializer(serializers.ModelSerializer):
    answers = AnswerCreateSerializer(many=True)

    class Meta:
        model = Response
        fields = ['survey', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = Response.objects.create(**validated_data)

        for answer_data in answers_data:
            selected_options = answer_data.pop('selected_options', [])
            answer = Answer.objects.create(response=response, **answer_data)
            if selected_options:
                answer.selected_options.set(selected_options)

        return response
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

