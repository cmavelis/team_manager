import requests
import json
import logging

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.utils import timezone

from .slack_messages import create_event
from .utils import send_slack_event_confirm
from team.models import Event, Player, Attendance

logger = logging.getLogger(__name__)


@csrf_exempt
def slack_test(request):
    if request.method == 'POST':
        payload = request.POST
    else:
        return Http404
    # print(payload)
    if payload['command'] == '/test_hi':
        response = {
            'text': 'Hi',
            'attachments': [
                {
                    'text': 'Sent by {}'.format(payload['user_name'])
                }
            ]
        }

        event = Event.objects.get(id=1)
        player = Player.objects.get(id=1)
        message_request = send_slack_event_confirm(event, player)
        r = requests.post('https://slack.com/api/chat.postMessage', params=message_request)
        print(r.content)
        return JsonResponse(response)


@csrf_exempt
def slack_create_event(request):
    if request.method == 'POST':
        payload = request.POST
    else:
        return Http404
    print(payload)
    if payload['command'] == '/create_event':
        event_name = payload['text']
        # Event.objects.create(name=event_name, type='T', date=timezone.now())

        response = {
            'text': 'Your event has been created',
            'attachments': [
                {
                    'text': 'Event name: {}'.format(event_name)
                }
            ]
        }

        return JsonResponse(create_event, safe=False)


@csrf_exempt
def slack_register(request):
    if request.method == 'POST':
        payload = request.POST
    else:
        return Http404
    print(payload)
    if payload['command'] == '/register':
        nickname = payload['text']
        found_player = get_object_or_404(Player, nickname=nickname)

        if not found_player.slack_user_id:
            found_player.slack_user_id = payload['user_id']
            found_player.save()
            response = {
                'text': 'Your account has been linked.',
                'attachments': [
                    {
                        'text': 'Webapp username: {}'.format(found_player.user)
                    }
                ]
            }
        else:
            response = {
                'text': 'This account is already linked to the webapp.',
                'attachments': [
                    {
                        'text': 'Webapp username: {}'.format(found_player.user)
                    }
                ]
            }

        return JsonResponse(response)

    else:
        return Http404


@csrf_exempt
def slack_my_events(request):
    if request.method == 'POST':
        payload = request.POST
    else:
        return Http404

    if payload['command'] == '/my_events':
        slack_user_id = payload['user_id']
        try:
            found_player = Player.objects.get(slack_user_id=slack_user_id)
        except Player.DoesNotExist:
            return JsonResponse({
                'text': 'Your Webapp account wasn\'t found.  '
                        'Have you registered your Slack ID yet? '
                        '\nUse /register [webapp nickname]',
            })

        event_list = Event.objects.all().order_by('date')
        attendance = found_player.attendance_set.all()
        attendance_entries = []
        for event in event_list:
            try:
                attendance_entries.append(attendance.get(event=event.id).get_status_display())
            except Attendance.DoesNotExist:
                attendance_entries.append('ERR')

        to_display = zip(event_list, attendance_entries)

        event_message = '*Event: Response*'
        for pair in to_display:
            pair_as_string = '\n%s: %s' % (pair[:])
            event_message += pair_as_string

        response = {
            'text': 'Your event responses:',
            'attachments': [
                {
                    'text': event_message
                }
            ]
        }

        return JsonResponse(response)

    else:
        return Http404


@csrf_exempt
def slack_interactive(request):
    if request.method == 'POST':
        payload = json.loads(request.POST['payload'])
    else:
        return Http404
    # logger.info(str(payload))
    print(payload)
    response = {
        'text': 'Interactive button pressed',
        'attachments': [
            {
                'text': 'Sent by {}'.format(payload['user']['username'])
            }
        ]
    }

    if payload['type'] == 'block_actions':
        user_input = payload['actions']
        new_message = {
            "token": payload['token'],
            "channel": payload['channel']['id'],
            "message": {
                "text": "Your response has been recorded as %s, thanks!" % 'TEST'
            }
        }
        r = requests.post('https://slack.com/api/chat.update', params=new_message)
        print(r.content)
        print(user_input[0]['value'])

    return JsonResponse(response)
