from datetime import datetime, timedelta
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum

from django.db.models import CharField, ForeignKey


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
        unique_together = ('vehicle_number', 'citizen_card', 'full_name', 'user')

    def __str__(self):
        return self.vehicle_number


class StorageLocker(BaseModel):
    number = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

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
    pickup_time = models.DateTimeField(null=True)
    quantity_items = models.IntegerField(default=1)
    thumbnail = CloudinaryField(null=True)
    description = RichTextField()
    package = models.ForeignKey(StorageLocker, on_delete=models.CASCADE)

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

class CommonNotification(BaseModel):
    title = models.CharField(max_length=100)
    content = RichTextField()

    def __str__(self):
        return self.title

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
    description = models.CharField(max_length=100)
    transaction = models.ForeignKey('Transaction',
                                    on_delete=models.CASCADE,
                                    null=True, blank=True,
                                    related_name='monthly_fees')

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


