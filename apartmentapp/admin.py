from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from apartmentapp.models import Reflection, User, MonthlyFee, Fee, Room, VehicleCard, RoomStatus


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

@admin.action(description='Lock users')
def lock_user(modeladmin, request, queryset):
    for room in queryset:
        try:
            if room.status == RoomStatus.AVAILABLE.value:
                modeladmin.message_user(request, f"Lock user in {room.room_number} fail!.", level="error")
            else:
                User.objects.filter(room=room, is_active=True).update(is_active=False, room=None)
                VehicleCard.objects.filter(user__room=room, user__is_active=False).update(active=False)
                room.status = RoomStatus.AVAILABLE.value
                room.save()
                modeladmin.message_user(request, f"Lock user in {room.room_number} success.", level="success")
        except Exception as ex:
            modeladmin.message_user(request, f"Error: {str(ex)}", level="error")



class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'status']
    actions = [lock_user]
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