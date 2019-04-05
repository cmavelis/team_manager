from django.urls import path

from . import views

app_name = 'slack_integration'
urlpatterns = [
    # slack/test/  slack test message
    path('test/', views.slack_test, name='slack_test'),
]
