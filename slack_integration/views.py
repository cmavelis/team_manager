import requests
import json
import logging

from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.utils.decorators import method_decorator

from .slack_messages import create_event
from .utils import send_slack_event_confirm, give_player_event_dropdowns, compose_message, replace_blocks_in_message
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

            # sending query when button is pressed #############################
            if action_id == 'send_message':
                filter_by_response = False
                if msg.player_id == 0:
                    players_to_message = list(Player.objects.filter(slack_user_id__isnull=False))
                    filter_by_response = True
                else:
                    players_to_message = [get_object_or_404(Player, id=msg.player_id)]

                # 0 means all pending events
                if msg.event_id == 0:
                    event_list = list(Event.objects.all())#.order_by('date'))  # TODO add a "this season" or "future" filter
                    event_text = 'All pending events'
                    filter_by_response = True
                else:
                    event_list = [get_object_or_404(Event, id=msg.event_id)]
                    event_text = get_object_or_404(Event, id=msg.event_id).name
                print(event_list, "  whole event list")

                messaged_player_names = []
                for player in players_to_message:
                    print(player)
                    attendance_to_query = Attendance.objects.filter(player=player, event__in=event_list)

                    if filter_by_response:
                        print([attendance_to_query])
                        attendance_to_query = attendance_to_query.filter(status__in=['P', 'U'])
                        print([attendance_to_query])
                        if attendance_to_query.count() == 0:
                            print('message not sent to %s' % player.nickname)
                            continue

                    events_to_query = list(Event.objects.filter(attendance__in=attendance_to_query).order_by('date'))
                    print('EVENT LIST')
                    print(event_list)
                    print('EVENTS TO QUERY')
                    print(events_to_query)

                    message_request, _ = send_slack_event_confirm(events_to_query, player)
                    # r = requests.post('https://slack.com/api/chat.postMessage', params=message_request) # TODO: re-enable message send
                    print('message sent to %s' % player.nickname)
                    print(message_request)
                    messaged_player_names.append(player.nickname)

                # update request text box to show what happened
                blocks = [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "You've sent a request to the following player(s) about *%s*:" % event_text
                                + ''.join(['\n• %s' % name for name in messaged_player_names])
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

            replacement_block = [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Your response has been recorded as *%s*, thanks!" % att_res_display
                }
            }]

            old_message_blocks = payload['message']['blocks']

            new_message_blocks = replace_blocks_in_message(old_message_blocks, block_id, replacement_block)

            message = compose_message(payload['container']['channel_id'],
                                      text='Succeeded',
                                      ts=original_time_stamp,
                                      blocks=json.dumps(new_message_blocks))
            r = requests.post('https://slack.com/api/chat.update', params=message)
            print(r.content)

    return JsonResponse(response)
