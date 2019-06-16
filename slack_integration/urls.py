from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'slack_integration'
urlpatterns = [
    # slack/interactive/  slack interactive message endpoint
    path('interactive/', csrf_exempt(views.SlackInteractiveView.as_view()), name='slack_interactive'),

    # slack/commands/  slack slash commands endpoint
    path('commands/', csrf_exempt(views.SlackCommandView.as_view()), name='slack_commands'),

    # slack/test/  slack test message
    path('test/', csrf_exempt(views.SlackCommandView.as_view()), name='slack_test'),

    # slack/create_event/  create an event from slack
    path('create_event/', views.slack_create_event, name='slack_create_event'),

    # slack/register/  register slack user id to webapp account  # TODO: change command url in Slack
    path('register/', csrf_exempt(views.SlackCommandView.as_view()), name='slack_register')
]
