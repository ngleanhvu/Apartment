from contextlib import nullcontext
from datetime import datetime, timedelta

from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum

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
    thumbnail = CloudinaryField(null=True)
    changed_password = models.BooleanField(default=False)

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
        default=RoomStatus.AVAILABLE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.room_number

class VehicleCard(BaseModel):
    full_name = models.CharField(max_length=100, null=False, default='')
    expiration_date = models.DateTimeField()
    vehicle_number = models.CharField(max_length=20, null=False, unique=True)
    relationship = models.CharField(
        max_length=30,
        choices=Relationship.choices(),
        default=Relationship.APARTMENT_OWNER
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.expiration_date:
            self.expiration_date = self.created_date + timedelta(days=365 * 3)
        super().save(*args, **kwargs)

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
        default=PackageStatus.NOT_RECEIVED
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
        default=ReflectionStatus.APPROVING
    )
    resolution = models.CharField(max_length=255, null=True, blank=True)
    resolved_date = models.DateTimeField(null=True)
    admin_resolved = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

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
        default=DeliveryMethod.APP
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

class Transaction(BaseModel):
    recipient_account_number = models.CharField(max_length=20)
    amount = models.FloatField(default=0)
    description = models.CharField(max_length=100)
    sender_account_number = models.CharField(max_length=100)
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices(),
        default=PaymentGateway.TRANSFER
    )
    thumbnail = CloudinaryField(null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fees = models.ManyToManyField('Fee', through='TransactionFee', related_name='transactions')

    def __str__(self):
        return self.amount

class Fee(BaseModel):
    name = models.CharField(max_length=50)
    unit_price = models.FloatField(default=0)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class TransactionFee(BaseModel):
    note = models.CharField(max_length=100)
    unit_price = models.FloatField(default=0)
    quantity = models.IntegerField(default=0)
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('fee', 'transaction')











