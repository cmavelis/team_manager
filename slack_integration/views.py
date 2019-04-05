from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.utils import timezone

from team.models import Event, Player


@csrf_exempt
def slack_test(request):
    if request.method == 'POST':
        payload = request.POST
    else:
        return Http404
    print(payload)
    if payload['command'] == '/test_hi':
        response = {
            'text': 'Hi',
            'attachments': [
                {
                    'text': 'Sent by {}'.format(payload['user_name'])
                }
            ]
        }

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
        Event.objects.create(name=event_name, type='T', date=timezone.now())

        response = {
            'text': 'Your event has been created',
            'attachments': [
                {
                    'text': 'Event name: {}'.format(event_name)
                }
            ]
        }

        return JsonResponse(response)


@csrf_exempt
def slack_register(request):
    if request.method == 'POST':
        payload = request.POST
    else:
        return Http404
    print(payload)
    if payload['command'] == '/webapp_register':
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

        return JsonResponse(response)

    else:
        return Http404
