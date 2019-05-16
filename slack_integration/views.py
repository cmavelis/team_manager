import requests
import json
import logging

from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.utils.decorators import method_decorator

from .slack_messages import create_event
from .utils import send_slack_event_confirm, give_player_event_dropdowns, compose_message
from team.models import Event, Player, Attendance
from users.models import AppUser
from team_manager import settings
from slack_integration.models import InteractiveMessage

logger = logging.getLogger(__name__)

# TODO: add token verification to all views (use mixin?)


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
        slack_user_id = payload['user_id']
        response = {}

        # if this Slack ID is already registered, tell the user that
        try:
            player = Player.objects.get(slack_user_id=slack_user_id)
            response['text'] = 'Your Slack account is already linked' \
                               ' to the web app with the email *%s*' % player.user.email

        # if this Slack ID isn't registered to an AppUser yet
        except Player.DoesNotExist:
            user_info_response = requests.get('https://slack.com/api/users.info',
                                              params={'user': slack_user_id, 'token': settings.SLACK_BOT_USER_TOKEN}
                                              )  # see https://api.slack.com/methods/users.info
            print(user_info_response.json())
            slack_profile = user_info_response.json()['user']['profile']
            user_email = slack_profile['email']

            # look for a user with the Slack-registered email to register with
            try:
                player = Player.objects.get(user__email=user_email)
                response['text'] = 'Your Slack account has been linked' \
                                   ' to the web app with the email *%s*' % player.user.email

            # otherwise create a user and link the Slack account
            except Player.DoesNotExist:
                new_user = AppUser.objects.create_user(email=user_email, full_name=slack_profile['real_name'])
                player = Player.objects.get(user=new_user)
                response['text'] = 'A web app account has been created for you' \
                                   ' with the email *%s* and linked to your Slack account' % player.user.email
            player.slack_user_id = slack_user_id
            player.save()
            # TODO: after creating AppUser and Player, send email with password

        return JsonResponse(response)

    else:
        return Http404


class SlackCommandView(View):
    def post(self, request):
        payload = request.POST
        command_name = payload['command'][1:].split(' ')[0]
        handler = getattr(self, 'handle_%s' % command_name)
        if not handler:
            return Http404
        print('handling command: %s' % command_name)
        return handler(payload)

    @staticmethod
    def handle_event_query(payload):
        new_ephemeral_message = give_player_event_dropdowns(channel=payload['user_id'])
        print(new_ephemeral_message)
        r = requests.post('https://slack.com/api/chat.postMessage', params=new_ephemeral_message)
        print(r.content)
        return HttpResponse(status=200)

    @staticmethod
    def handle_my_events(payload):
        slack_user_id = payload['user_id']
        try:
            found_player = Player.objects.get(slack_user_id=slack_user_id)
        except Player.DoesNotExist:
            return JsonResponse({
                'text': 'Your web app account wasn\'t found.  '
                        'Have you registered your Slack ID yet? '
                        '\nType in: /register',
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

        attachment_text = ''
        for pair in to_display:
            event = pair[0]
            event_and_attendance_string = '*%s*: %s\n' % (pair[:])
            attachment_text += event_and_attendance_string + event.date.strftime('%B %d %Y') + '\n\n'

        # TODO: add an option for editing responses attached to this message
        response = {
            'text': 'Your event responses:',
            'attachments': [
                {'text': attachment_text}
            ]
        }

        return JsonResponse(response)


@csrf_exempt
def slack_interactive(request):
    if request.method == 'POST':
        payload = json.loads(request.POST['payload'])
    else:
        return Http404
    print(payload)
    response = {
        'text': 'Interactive action received',
        'attachments': [
            {
                'text': 'Sent by {}'.format(payload['user']['username'])
            }
        ]
    }

    if payload['type'] == 'block_actions':
        original_time_stamp = payload['container']['message_ts']
        block_id = payload['actions'][0]['block_id']

        # event request dropdowns handling
        if block_id.startswith('event_rq_dropdowns'):
            # find or create message DB entry
            try:
                msg = InteractiveMessage.objects.get(slack_message_ts=original_time_stamp)
            except InteractiveMessage.DoesNotExist:
                msg = InteractiveMessage.objects.create(slack_message_ts=original_time_stamp)

            action_id = payload['actions'][0]['action_id']

            # sending query when button is pressed
            if action_id == 'send_message':
                event = ''
                player_list = []
                # 0 means all pending events
                if msg.event_id == 0:
                    event_list = list(Event.objects.all().order_by('date'))
                else:
                    event_list = [Event.objects.get(id=msg.event_id)]
                print(event_list, "  whole event list")

                for event in event_list:
                    print(event, "  in event list")
                    # 0 means all pending players
                    if msg.player_id == 0:
                        all_pending_attendance = Attendance.objects.filter(event=event,
                                                                           status__in=['P', 'U'],
                                                                           player__slack_user_id__isnull=False)
                        player_list = [attendance.player for attendance in all_pending_attendance]
                    else:
                        player_list = [Player.objects.get(id=msg.player_id)]

                    for player in player_list:
                        print(player)
                        message_request, _ = send_slack_event_confirm(event, player)
                        r = requests.post('https://slack.com/api/chat.postMessage', params=message_request)
                        print('message sent to player')

                # update request text box to show what happened
                event_text = 'All pending events' if msg.event_id == 0 else event.name
                blocks = [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "You've sent a request to the following player(s) about *%s*:" % event_text
                                + ''.join(['\n• %s' % p.nickname for p in player_list])
                    }
                }]

                message = compose_message(channel=payload['container']['channel_id'],
                                          ts=original_time_stamp,
                                          text='Sent',
                                          blocks=json.dumps(blocks),
                                          user=payload['user']['id'],
                                          as_user=True)
                r = requests.post('https://slack.com/api/chat.update', params=message)

                return JsonResponse({
                    'response_type': 'message',
                    'text': '',
                    'replace_original': True,
                    'delete_original': True,
                    'as_user': True,
                })

            # add response info to message object
            action_value = payload['actions'][0]['selected_option']['value']
            if action_id == 'player_id':
                msg.player_id = action_value
                msg.save()
            elif action_id == 'event_id':
                msg.event_id = action_value
                msg.save()

        # handling response back from player
        if block_id.startswith('event_rq_response'):
            user_input = payload['actions'][0]
            attendance_response = user_input['value']
            event_responded_id = block_id.split('_')[-1]
            att_res_display = dict(Attendance.ATTENDANCE_TYPES)[attendance_response]

            # msg = get_object_or_404(InteractiveMessage, id=block_id.split('_')[-1])
            print('message found')
            attendance = get_object_or_404(Attendance, event=event_responded_id,
                                           player__slack_user_id=payload['user']['id'])
            print('attn found')

            # attempting to update attendance database entry
            attendance.status = attendance_response
            attendance.save()
            blocks = [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Your response has been recorded as *%s*, thanks!" % att_res_display
                }
            }]

            message = compose_message(payload['container']['channel_id'],
                                      text='Succeeded',
                                      ts=original_time_stamp,
                                      blocks=json.dumps(blocks))
            r = requests.post('https://slack.com/api/chat.update', params=message)
            print(r.content)

    return JsonResponse(response)
