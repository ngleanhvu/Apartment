from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from apartmentapp.models import Reflection, User, StorageLocker, Package


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

admin_site.register(Reflection, ReflectionAdmin)
admin_site.register(User)
admin_site.register(StorageLocker, StorageLockerAdmin)
admin_site.register(Package, PackageAdmin)
