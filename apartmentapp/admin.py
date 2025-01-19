from django.db import transaction
from django.db.models import Count
from django.template.response import TemplateResponse
from ckeditor.widgets import CKEditorWidget
from calendar import month
from datetime import datetime

import requests
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib import admin
from django import forms
from rest_framework import status

from django.contrib import messages
from apartmentapp.models import Reflection, User, StorageLocker, Package, Feedback, FeedbackResponse, Survey, Question, \
    QuestionOption, Response, MonthlyFee, Fee, Room, VehicleCard, RoomStatus, Transaction, PackageStatus, FeedbackStatus
from django.utils.safestring import mark_safe
from django.urls import path

from apartmentapp.models import Reflection, User, MonthlyFee, Fee, Room, VehicleCard, RoomStatus, Transaction, \
    CommonNotification


# Register your models here.

class ApartmentAdminSite(admin.AdminSite):
    site_header = 'Apartment Management'

    def get_urls(self):
        return [path('survey-stats/', self.stats_view)] + super().get_urls()

    def stats_view(self, request):
        surveys = Survey.objects.filter(active=True)
        survey_id = request.GET.get('survey')

        if not survey_id:
            survey_id = surveys.first().id

        responses = Response.objects.filter(survey__id=survey_id).values('question','question_option','question__content','question_option__content').annotate(counter=Count('resident', distinct=True)).order_by('question', 'question_option')
        sum_resident_in_survey=Response.objects.filter(survey__id=survey_id).values('resident').distinct().count()

        stats = {}
        for response in responses:
            question_content = response['question__content']

            if question_content not in stats:
                stats[question_content] = {
                    'options': []
                }

            stats[question_content]['options'].append({
                'content': response['question_option__content'],
                'count': response['counter']
            })


        question_totals = {}
        for question_content, data in stats.items():
            question_totals[question_content] = sum(opt['count'] for opt in data['options'])

        print(stats)

        return TemplateResponse(request, 'admin/stats.html',
                                {'stats': stats, 'question_totals': question_totals, 'surveys': surveys, 'sum' : sum_resident_in_survey})


admin_site = ApartmentAdminSite('myapartment')

# Additional action
@admin.action(description='Khóa tài khoản của người dùng trong phòng')
def lock_user(modeladmin, request, queryset):
    for room in queryset:
        try:
            if room.status == RoomStatus.AVAILABLE.value:
                modeladmin.message_user(request, f"Lock user in {room.room_number} fail!.", level="error")
            else:
                User.objects.filter(room=room, is_active=True).update(is_active=False, room=None, changed_password=False)
                VehicleCard.objects.filter(user__room=room, user__is_active=False).update(active=False)
                room.status = RoomStatus.AVAILABLE.value
                room.save()
                modeladmin.message_user(request, f"Lock user in {room.room_number} success.", level="success")
        except Exception as ex:
            modeladmin.message_user(request, f"Error: {str(ex)}", level="error")


@admin.action(description="Tính phí dịch vụ hằng tháng cho tất cả các phòng")
def calculate_service_fee(modeladmin, request, queryset):
    try:
        fee = Fee.objects.filter(name="Phí quản lý").first()

        monthly_fees = []

        for room in queryset:
            if room.status == RoomStatus.AVAILABLE.value:
                continue

            monthly_fee = MonthlyFee(fee=fee,
                                     amount=fee.value,
                                     room=room,
                                     description=f"Phí dịch vụ tháng {datetime.now().month} năm {datetime.now().year} phòng {room.room_number}")
            monthly_fees.append(monthly_fee)

        MonthlyFee.objects.bulk_create(monthly_fees)
        modeladmin.message_user(request, 'Tính toán thành công', level="success")
    except Exception as ex:
        modeladmin.message_user(request, f"Error: {str(ex)}", level="error")

@admin.action(description="Tính phí giữ xe hằng tháng cho tất cả các phòng")
def calculate_parking_fee(modeladmin, request, queryset):
    try:
        fee = Fee.objects.filter(name="Phí giữ xe").first()

        monthly_fees = []

        for room in queryset:
            vehicle_count = VehicleCard.objects.filter(user__room=room, active=True).count()
            if vehicle_count > 0:
                monthly_fee = MonthlyFee(fee=fee,
                                         room=room,
                                         amount=fee.value*vehicle_count,
                                         description=f"Phí giữ xe tháng {datetime.now().month} năm {datetime.now().year} phòng {room.room_number}")
                monthly_fees.append(monthly_fee)

        MonthlyFee.objects.bulk_create(monthly_fees)

        modeladmin.message_user(request, 'Tính toán thành công', level="success")

    except Exception as ex:
        modeladmin.message_user(request, f"Error: {str(ex)}", level="error")


class ReflectionForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Reflection
        fields = '__all__'


class PackageForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Package
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
    actions = [lock_user, calculate_service_fee, calculate_parking_fee]

    form_args = {
        'user': {
            'validators': []
        }
    }

class VehicleCardAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'user']
    readonly_fields = ['vehicle_number', 'user']

class MonthlyFeeInline(admin.TabularInline):
    model = MonthlyFee
    extra = 1

class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    inlines = [MonthlyFeeInline]
    # fields = ['amount', 'payment_gateway', 'user', 'thumbnail']
    readonly_fields = ['avatar']

    def avatar(self, transaction):
        return mark_safe("<img src='{img_url}' alt='{alt}' width='120' />".format(
            img_url=transaction.thumbnail.url,
            alt=transaction.user.full_name
        ))


EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def send_push_notification(expo_push_token, title, message):
    payload = {
        "to": expo_push_token,
        "title": title,
        "body": message,
    }
    response = requests.post(EXPO_PUSH_URL, json=payload)
    return response.json()

class CommonNotificationAdmin(admin.ModelAdmin):
    class Meta:
        model = CommonNotification
        fields = '__all__'

class StorageLockerAdmin(admin.ModelAdmin):
    list_display = ['number', 'created_date', 'user' ,'active']
    search_fields = ['number', 'user__phone', 'user__full_name']

class PackageAdmin(admin.ModelAdmin):
    form=PackageForm
    list_display = ['storage_locker', 'sender_name', 'recipient_name','pickup_time', 'quantity_items','description','display_thumbnail','status']
    search_fields = ['storage_locker__number', 'storage_locker__user__phone']
    list_filter = ['storage_locker__number', 'storage_locker__user__phone']
    readonly_fields = ['thumbnail_preview']
    actions = ['change_status']


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        obj.send_sms()


    @admin.action(description="Xác nhận đã nhận hàng")
    def change_status(self, request, queryset):
        for package in queryset:
            if package.status == PackageStatus.NOT_RECEIVED.value:
                package.status = PackageStatus.RECEIVED.value
                package.pickup_time = datetime.now()
                package.save()
                messages.success(request, f"Package {package.id} status updated to RECEIVED.")
            else:
                messages.warning(request, f"Package {package.id} is already RECEIVED.")

    def thumbnail_preview(self, package):
        if package.thumbnail:
            cloudinary_url = "https://res.cloudinary.com/dea1l3vvu/{}".format(package.thumbnail)
            return mark_safe('<img src="{img_url}" width="250" alt="{alt}" />'.format(
                img_url=cloudinary_url,
                alt='No image uploaded'
            ))
        return "No image uploaded"
    thumbnail_preview.short_description = 'Thumbnail Preview'

    def display_thumbnail(self, package):
        if package.thumbnail:
            cloudinary_url = "https://res.cloudinary.com/dea1l3vvu/{}".format(package.thumbnail)
            return mark_safe('<img src="{img_url}" width="100" height="50" alt="{alt}" />'.format(
                img_url=cloudinary_url,
                alt='No image'
            ))
        return "No image"
    display_thumbnail.short_description = 'Thumbnail'

class FeedBackAdminInline(admin.StackedInline):
    model = FeedbackResponse

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'status', 'resident']
    search_fields = ['resident__phone', 'status']
    filter = ['created_date']
    actions = ['respond_action']
    inlines = [FeedBackAdminInline]

    @admin.action(description="Xác nhận đã giải quyết phản ánh")
    def respond_action(self, request, queryset):
        resolved_count = 0
        for feedback in queryset:
            if feedback.status == FeedbackStatus.RESOLVED.value:
                self.message_user(
                    request,
                    f"Feedback '{feedback.title}' đã được giải quyết!",
                    level=messages.WARNING
                )
                continue

            feedback.status = FeedbackStatus.RESOLVED.value
            feedback.save()
            resolved_count += 1

        if resolved_count:
            self.message_user(
                request,
                f"{resolved_count} phản ánh đã được đánh dấu là RESOLVED.",
                level=messages.SUCCESS
            )

class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ['feedback', 'response', 'admin']
    search_fields = ['feedback__resident__phone']
    filter=['created_date']

#Survey
class QuestionInlineAdmin(admin.StackedInline):
    model=Question
    fk_name = 'survey'

# class QuestionOptionInlineAdmin(admin.StackedInline):
#     model = QuestionOption
#     fk_name = 'question'

class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'status', 'description']
    search_fields = ['status', 'title']
    list_filter =['start_date', 'status']
    ordering = ['start_date', 'end_date']
    inlines = (QuestionInlineAdmin, )

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['content', 'survey']
    search_fields = ['survey__title']
    filter=['survey']
    ordering = ['survey']
    #inlines = (QuestionOptionInlineAdmin, )

class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['content']
    search_fields = ['question']
    filter=['question__survey']


class ResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'resident', 'question_option', 'question']
    list_filter = ['survey']
    search_fields = ['resident__full_name', 'survey__title']

# class AnswerAdmin(admin.ModelAdmin):
#     list_display = ['question', 'response', 'text_answer', 'boolean_answer', 'display_selected_options']
#     list_filter = ['question__survey', 'response__resident', 'question__type']
#     search_fields = ['question__content']
#
#     def display_selected_options(self, obj):
#         return ", ".join([str(option) for option in obj.selected_options.all()])
#     display_selected_options.short_description = 'Selected Options'


admin_site.register(Reflection, ReflectionAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(MonthlyFee, MonthlyFeeAdmin)
admin_site.register(Fee, FeeAdmin)
admin_site.register(Room, RoomAdmin)
admin_site.register(VehicleCard, VehicleCardAdmin)
admin_site.register(Transaction, TransactionAdmin)
admin_site.register(CommonNotification, CommonNotificationAdmin)
admin_site.register(StorageLocker, StorageLockerAdmin)
admin_site.register(Package, PackageAdmin)
#
admin_site.register(Feedback, FeedbackAdmin)
admin_site.register(FeedbackResponse, FeedbackResponseAdmin)
#
admin_site.register(Survey, SurveyAdmin)
admin_site.register(Question, QuestionAdmin)
admin_site.register(QuestionOption, QuestionOptionAdmin)
admin_site.register(Response, ResponseAdmin)