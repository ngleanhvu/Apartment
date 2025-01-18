from rest_framework import pagination

class MonthlyFeePagination(pagination.PageNumberPagination):
    page_size = 6

class PackagePagination(pagination.PageNumberPagination):
    page_size = 2