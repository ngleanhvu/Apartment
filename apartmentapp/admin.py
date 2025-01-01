from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from apartmentapp.models import Reflection, User, MonthlyFee, Transaction, TransactionMonthlyFee, Fee, Room


# Register your models here.

class ApartmentAdminSite(admin.AdminSite):
    site_header = 'Apartment Management'

admin_site = ApartmentAdminSite('myapartment')

class ReflectionForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Reflection
        fields = '__all__'

class ReflectionAdmin(admin.ModelAdmin):
    form = ReflectionForm
    list_display = ['title', 'content', 'resolution']
    search_fields = ['title', 'resolved_date']
    list_filter = ['user__full_name']

class UserAdmin(admin.ModelAdmin):
    readonly_fields = ['avatar']

    def avatar(self, user):
        return mark_safe("<img src='/static/{img_url}' alt='{alt}' width='120' />".format(
            img_url=user.thumbnail.name,
            alt=user.full_name
        ))

class FeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

class MonthlyFeeAdmin(admin.ModelAdmin):
    list_display = ['amount', 'status', 'room', 'fee']
    list_filter = ['status', 'room__room_number', 'fee__name', 'created_date']
    search_fields = ['status', 'created_date', 'room__room_number', 'fee__name']

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['amount', 'description', 'payment_gateway', 'created_date', 'user', 'room']

class TransactionMonthlyFeeAdmin(admin.ModelAdmin):
    list_display = ['amount', 'transaction', 'monthly_fee', 'created_date']

class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'status', ]

    form_args = {
        'user': {
            'validators': []
        }
    }

admin_site.register(Reflection, ReflectionAdmin)
admin_site.register(User)
admin_site.register(MonthlyFee, MonthlyFeeAdmin)
admin_site.register(Transaction, TransactionAdmin)
admin_site.register(TransactionMonthlyFee, TransactionMonthlyFeeAdmin)
admin_site.register(Fee, FeeAdmin)
admin_site.register(Room, RoomAdmin)