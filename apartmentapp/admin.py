from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from apartmentapp.models import Reflection, User
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

admin_site.register(Reflection, ReflectionAdmin)
admin_site.register(User)