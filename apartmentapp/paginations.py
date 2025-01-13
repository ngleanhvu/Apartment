from rest_framework import pagination

class MonthlyFeePagination(pagination.PageNumberPagination):
    page_size = 5

class PackagePagination(pagination.PageNumberPagination):
    page_size = 2