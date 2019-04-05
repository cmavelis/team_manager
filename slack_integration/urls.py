from django.urls import path

from . import views

app_name = 'slack_integration'
urlpatterns = [
    # slack/test/  slack test message
    path('test/', views.slack_test, name='slack_test'),

    # slack/create_event/  create an event from slack
    path('create_event/', views.slack_create_event, name='slack_create_event'),

    # slack/register/  register slack user id to webapp account
    path('register/', views.slack_register, name='slack_register')
]
