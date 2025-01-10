from rest_framework import permissions


class OwnerPerms(permissions.IsAuthenticated):
    # Kiem tra quyen tong quat xem nguoi dung da dang nhap chua
    def has_permission(self, request, view):
        return super().has_permission(request, view)

    # Neu da dang nhap thanh cong thi kiem tra nguoi dung dang nhap phai la chu so huu
    def has_object_permission(self, request, view, obj):
        is_authenticated = self.has_permission(request, view)
        is_owner = request.user == obj.user
        return is_owner and is_authenticated


class TransactionPerms(permissions.IsAuthenticated):
    # Kiem tra user da dang nhap hay chua
    # Kiem tra user co thuoc phong do khong va user hien tai dang con o trong chung cu hay khong
    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and obj.room == request.user.room

class MonthlyFeePerms(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and obj.room == request.user.room
