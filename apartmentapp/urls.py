from os.path import basename

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import MonthlyFeeViewSet

# Ten API de so nhieu de theo chuan thiet ke RESTFull API
r = DefaultRouter()
r.register('users', views.UserViewSet, basename='users')
r.register('transactions', views.TransactionViewSet, basename='transactions')
r.register('vehicle-cards', views.VehicleCardViewSet, basename='vehicle-cards')
r.register('storage_lockers', views.StorageLockerViewSet, 'storage_lockers')
r.register('packages', views.PackageViewSet, 'packages')
r.register('feedbacks', views.FeedbackViewSet,'feedbacks')
#r.register('feedback_responses', views.FeedbackResponseViewSet, 'feedback_responses')
r.register('surveys', views.SurveyViewSet, 'surveys')
# r.register('questions', views.QuestionViewSet, 'questions')
# r.register('question_options', views.QuestionOptionViewSet, 'question_options')
# r.register('answers', views.AnswerViewSet, 'answers')
r.register('responses', views.ResponseViewSet, 'responses')

r.register('fees', views.FeeViewSet, basename='fees')
urlpatterns = [
    path('', include(r.urls)),
    path('monthly-fees/fees/<int:fee_id>/', MonthlyFeeViewSet.as_view({'get': 'list'})),
    path('monthly-fees/pending/', MonthlyFeeViewSet.as_view({'get': 'list_monthly_fee_pending'}))
]
