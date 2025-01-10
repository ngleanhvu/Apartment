from contextlib import nullcontext
from datetime import datetime, timedelta
from random import choice
from tkinter.constants import CASCADE

from aiohttp.web_urldispatcher import Resource
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum

from django.db.models import CharField, ForeignKey, Model


# Create your models here

class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Relationship(Enum):
    APARTMENT_OWNER = 'Apartment owner'
    RELATIVE = 'Relative'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class User(AbstractUser):
    full_name = models.CharField(max_length=100, null=False)
    phone = models.CharField(max_length=15, null=False, unique=True)
    date_of_birth = models.DateTimeField(auto_now=False, null=True)
    gender = models.BooleanField(default=True)
    citizen_card = models.CharField(max_length=15, null=False, unique=True)
    thumbnail = CloudinaryField(null=True, blank=True)
    changed_password = models.BooleanField(default=False)
    room = models.ForeignKey('Room', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.full_name


class RoomStatus(Enum):
    AVAILABLE = 'Available'
    OCCUPIED = 'Occupied'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class Room(BaseModel):
    room_number = models.CharField(max_length=20, null=False, unique=True)
    area = models.FloatField(default=0)
    floor = models.IntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=RoomStatus.choices(),
        default=RoomStatus.AVAILABLE.value
    )
    unit_price = models.FloatField(default=0)

    def __str__(self):
        return self.room_number


class VehicleCard(BaseModel):
    vehicle_number = models.CharField(max_length=20, null=False, unique=True)
    relationship = models.CharField(
        max_length=20,
        choices=Relationship.choices(),
        default=Relationship.APARTMENT_OWNER.value
    )
    full_name = models.CharField(null=False, max_length=50)
    citizen_card = models.CharField(null=False, max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('vehicle_number', 'citizen_card', 'active', 'user')

    def __str__(self):
        return self.vehicle_number


class StorageLocker(BaseModel):
    number = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='storage_locker')

    def __str__(self):
        return self.number


class PackageStatus(Enum):
    NOT_RECEIVED = 'Not received'
    RECEIVED = 'Received'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class Package(BaseModel):
    sender_name = models.CharField(max_length=50)
    recipient_name = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=PackageStatus.choices(),
        default=PackageStatus.NOT_RECEIVED.value
    )
    pickup_time = models.DateTimeField(null=True, blank=True)
    quantity_items = models.IntegerField(default=1)
    thumbnail = CloudinaryField(null=True)
    description = RichTextField()
    storage_locker = models.ForeignKey(StorageLocker, on_delete=models.CASCADE, related_name='packages')

    def __str__(self):
        return self.description

class ReflectionStatus(Enum):
    APPROVED = 'Approved'
    SOLVED = 'Solved'
    APPROVING = 'Approving'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]

class Reflection(BaseModel):
    title = models.CharField(max_length=100)
    content = RichTextField()
    status = models.CharField(
        max_length=20,
        choices=ReflectionStatus.choices(),
        default=ReflectionStatus.APPROVING.value
    )
    resolution = models.CharField(max_length=255, null=True, blank=True)
    resolved_date = models.DateTimeField(null=True)
    admin_resolved = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class DeliveryMethod(Enum):
    APP = 'App'
    SMS = 'SMS'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]

class CommonNotification(BaseModel):
    title = models.CharField(max_length=100)
    content = RichTextField()
    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices(),
        default=DeliveryMethod.APP.value
    )

    def __str__(self):
        return self.title


class PrivateNotification(CommonNotification):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class PaymentGateway(Enum):
    TRANSFER = 'Transfer'
    STRIPE = 'Stripe'
    MOMO = 'Momo'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class TransactionStatus(Enum):
    PENDING = 'Pending'
    SUCCESS = 'Success'
    FAIL = 'Fail'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class Fee(BaseModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    value = models.FloatField(default=0)

    def __str__(self):
        return self.name


class MonthlyFeeStatus(Enum):
    PENDING = 'Pending'
    PAID = 'Paid'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class MonthlyFee(BaseModel):
    amount = models.FloatField(default=0)
    status = models.CharField(
        max_length=20,
        choices=MonthlyFeeStatus.choices(),
        default=MonthlyFeeStatus.PENDING.value
    )
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    fee = models.ForeignKey(Fee, on_delete=models.SET_NULL, null=True)
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('room', 'fee', 'created_date', 'status', 'transaction')


class Transaction(BaseModel):
    amount = models.FloatField(default=0)
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices(),
        default=PaymentGateway.MOMO.value
    )
    description = models.CharField(max_length=255)
    thumbnail = CloudinaryField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices(),
        default=TransactionStatus.PENDING.value
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.full_name

#FEEDBACK
class FeedbackStatus(Enum):
    IN_PROGRESS= 'In progress'
    RESOLVED= 'Resolved'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]

class Feedback(BaseModel):
    title=models.CharField(max_length=200)
    description=RichTextField()
    status = models.CharField(max_length=20,
                              choices=FeedbackStatus.choices(),
                              default=FeedbackStatus.IN_PROGRESS.value)

    resident=models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')

    def __str__(self):
        return self.title

class FeedbackResponse(BaseModel):
    response=RichTextField()

    admin=models.ForeignKey(User, on_delete=models.PROTECT)
    feedback=models.OneToOneField(Feedback, on_delete=models.CASCADE,  related_name='response')

#SURVEY
class SurveyStatusEnum(Enum):
    PUBLISHED = 'Published'
    CLOSED = 'Closed'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]

class QuestionTypeEnum(Enum):
    MULTIPLE_CHOICE='Multiple choice'
    SINGLE_CHOICE='Single choice'
    TEXT='Text'
    YES_NO='Yes/No'

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]

class Survey(BaseModel):
    title=models.CharField(max_length=200)
    description=models.TextField()
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()
    status=models.CharField(max_length=20,
                            choices=SurveyStatusEnum.choices(),
                            default=SurveyStatusEnum.PUBLISHED.value)

    created_by=models.ForeignKey(User, on_delete=models.PROTECT, related_name='surveys')

    def __str__(self):
        return self.title

class Question(BaseModel):
    content=models.TextField()
    type=models.CharField(max_length=20, choices=QuestionTypeEnum.choices(),
                          default=QuestionTypeEnum.MULTIPLE_CHOICE.value)
    survey=models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.content

class QuestionOption(BaseModel): #For multiple choices and single choice
    question=models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    content=models.TextField()

    def __str__(self):
        return self.content

class Response(BaseModel):
    survey=models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    resident=models.ForeignKey(User, on_delete=models.PROTECT, related_name='survey_responses')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resident.full_name}'s response to {self.survey.title}"

class Answer(BaseModel):
    text_answer=models.TextField(null=True, blank=True)
    boolean_answer=models.BooleanField(null=True,blank=True)

    selected_options=models.ManyToManyField(QuestionOption, related_name='answers', null=True, blank=True)
    response=models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question=models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')

    def __str__(self):
        return f"Answer to {self.question.content}"










