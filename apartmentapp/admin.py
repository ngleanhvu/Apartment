from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from apartmentapp.models import Reflection, User, MonthlyFee, Fee, Room, VehicleCard


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
        return mark_safe("<img src='{img_url}' alt='{alt}' width='120' />".format(
            img_url=user.thumbnail.url,
            alt=user.full_name
        ))

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


class FeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


class MonthlyFeeAdmin(admin.ModelAdmin):
    list_display = ['amount', 'status', 'room', 'fee']
    list_filter = ['status', 'room__room_number', 'fee__name', 'created_date']
    search_fields = ['status', 'created_date', 'room__room_number', 'fee__name']
    readonly_fields = ['transaction']


class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'status']

    form_args = {
        'user': {
            'validators': []
        }
    }

class VehicleCardAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'user']
    readonly_fields = ['vehicle_number', 'user']

admin_site.register(Reflection, ReflectionAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(MonthlyFee, MonthlyFeeAdmin)
admin_site.register(Fee, FeeAdmin)
admin_site.register(Room, RoomAdmin)
admin_site.register(VehicleCard, VehicleCardAdmin)