from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from apartmentapp.models import Reflection, User, StorageLocker, Package, Feedback, FeedbackResponse, Survey, Question, \
    QuestionOption, Response, Answer, QuestionTypeEnum


# Register your models here.

class ApartmentAdminSite(admin.AdminSite):
    site_header = 'Apartment Management'

admin_site = ApartmentAdminSite('myapartment')

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
        return mark_safe("<img src='/static/{img_url}' alt='{alt}' width='120' />".format(
            img_url=user.thumbnail.name,
            alt=user.full_name
        ))

class StorageLockerAdmin(admin.ModelAdmin):
    list_display = ['number', 'created_date', 'user' ,'active']
    search_fields = ['number', 'user__phone', 'user__full_name']

class PackageAdmin(admin.ModelAdmin):
    form=PackageForm
    list_display = ['storage_locker', 'sender_name', 'recipient_name','pickup_time', 'quantity_items','description','display_thumbnail','status']
    search_fields = ['storage_locker__number', 'storage_locker__user__phone']
    list_filter = ['storage_locker__number', 'storage_locker__user__phone']
    readonly_fields = ['thumbnail_preview']

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

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'status', 'resident']
    search_fields = ['resident__phone', 'status']
    filter = ['created_date']

class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ['feedback', 'response', 'admin']
    search_fields = ['feedback__resident__phone']
    filter=['created_date']

#Survey
class QuestionInlineAdmin(admin.StackedInline):
    model=Question
    fk_name = 'survey'

class QuestionOptionInlineAdmin(admin.StackedInline):
    model = QuestionOption
    fk_name = 'question'

class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'status', 'description']
    search_fields = ['status', 'title']
    list_filter =['start_date', 'status']
    ordering = ['start_date', 'end_date']
    inlines = (QuestionInlineAdmin, )

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['content', 'type', 'survey']
    search_fields = ['survey__title', 'type']
    filter=['survey', 'type']
    ordering = ['survey']
    inlines = (QuestionOptionInlineAdmin, )

class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['content', 'question']
    search_fields = ['question']
    filter=['question__survey']
    ordering = ['question']


class ResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'resident', 'submitted_at']
    list_filter = ['submitted_at', 'survey']
    search_fields = ['resident__full_name', 'survey__title']

class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'response', 'text_answer', 'boolean_answer', 'display_selected_options']
    list_filter = ['question__survey', 'response__resident', 'question__type']
    search_fields = ['question__content']

    def display_selected_options(self, obj):
        return ", ".join([str(option) for option in obj.selected_options.all()])
    display_selected_options.short_description = 'Selected Options'


admin_site.register(Reflection, ReflectionAdmin)
admin_site.register(User)
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
admin_site.register(Answer, AnswerAdmin)