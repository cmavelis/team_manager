import requests
import json
import logging
import re

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse

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
    def __init__(self):
        self.payload = None
        self.slack_user_id = None
        self.command_text = None
        super(SlackCommandView, self).__init__()

    def post(self, request):
        payload = request.POST
        self.payload = payload
        self.slack_user_id = payload['user_id']
        command_name = payload['command'][1:].split(' ')[0]
        self.command_text = payload['text']
        print(payload['command'])
        handler = getattr(self, 'handle_%s' % command_name)
        if not handler:
            return Http404
        print('handling command: %s' % command_name)
        return handler()

    def handle_event_query(self):
        new_ephemeral_message = give_player_event_dropdowns(channel=self.slack_user_id)
        print(new_ephemeral_message)
        r = requests.post('https://slack.com/api/chat.postMessage', params=new_ephemeral_message)
        print(r.content)
        return HttpResponse(status=200)

    def handle_my_events(self):
        try:
            found_player = Player.objects.get(slack_user_id=self.slack_user_id)
            who_text = 'Your'
        except Player.DoesNotExist:
            return JsonResponse({
                'text': 'Your web app account wasn\'t found.  '
                        'Have you registered your Slack ID yet? '
                        '\nType in: /register',
            })

        if self.command_text:
            if found_player.captain_status:
                match = re.search('@U\w*', self.command_text)
                user_to_find = match.group()[1:]
                try:
                    found_player = Player.objects.get(slack_user_id=user_to_find)
                    who_text = found_player.nickname + '\'s'
                except Player.DoesNotExist:
                    return JsonResponse({
                        'text': 'User not found',
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
            'text': '%s event responses:' % who_text,
            'attachments': [
                {'text': attachment_text}
            ]
        }

        return JsonResponse(response)


class SlackInteractiveView(View):
    def __init__(self):
        self.payload = None
        self.original_time_stamp = None
        self.action_id = None
        self.action_detail = None
        super(SlackInteractiveView, self).__init__()

    def post(self, request):
        self.payload = json.loads(request.POST['payload'])
        self.original_time_stamp = self.payload['container']['message_ts']
        self.action_id = self.payload['actions'][0]['action_id']

        block_id = self.payload['actions'][0]['block_id']
        # block id looks like this: 'action_name_here_then-detail'
        action_name = block_id.split('-')[0]
        self.action_detail = block_id.split('-')[-1]

        handler = getattr(self, 'handle_%s' % action_name)
        if not handler:
            return Http404
        print('handling command: %s' % action_name)
        return handler()

    def get_database_message(self):
        # find or create message DB entry
        try:
            return InteractiveMessage.objects.get(slack_message_ts=self.original_time_stamp)
        except InteractiveMessage.DoesNotExist:
            return InteractiveMessage.objects.create(slack_message_ts=self.original_time_stamp)

    def handle_event_rq_dropdowns_select(self):
        # add selected player or event info to message object
        action_value = self.payload['actions'][0]['selected_option']['value']
        msg = self.get_database_message()

        if self.action_id == 'player_id':
            msg.player_id = action_value
            msg.save()
        elif self.action_id == 'event_id':
            msg.event_id = action_value
            msg.save()

        return HttpResponse(status=200)

    def handle_event_rq_dropdowns_send(self):
        msg = self.get_database_message()

        messaged_list = set()
        status_list = ['P', 'Y', 'N', 'U']
        # 0 means all pending events
        if msg.event_id == 0:
            event_list = list(Event.objects.all().order_by('date'))
            status_list = ['P', 'U']
        else:
            event_list = [Event.objects.get(id=msg.event_id)]
        print(event_list, "  whole event list")

        # 0 means all pending players
        if msg.player_id == 0:
            player_list = list(Player.objects.all())
            status_list = ['P', 'U']
        else:
            player_list = [Player.objects.get(id=msg.player_id)]

        for player in player_list:
            print(player)
            for attendance in list(Attendance.objects.filter(player=player,
                                                             event__in=event_list,
                                                             status__in=status_list,
                                                             player__slack_user_id__isnull=False)
                                           .order_by('event__date')):
                message_request, _ = send_slack_event_confirm(attendance.event, player)
                r = requests.post('https://slack.com/api/chat.postMessage', params=message_request)
                print('message sent to player')
                messaged_list.add(player)

        # update request text box to show what happened
        event_text = 'All pending events' if msg.event_id == 0 else event_list[0].name
        blocks = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "You've sent a request to the following player(s) about *%s*:" % event_text
                        + ''.join(['\n• %s' % p.nickname for p in player_list])
            }
        }]

        message = compose_message(channel=self.payload['container']['channel_id'],
                                  ts=self.original_time_stamp,
                                  text='Sent',
                                  blocks=json.dumps(blocks),
                                  user=self.payload['user']['id'],
                                  as_user=True)
        r = requests.post('https://slack.com/api/chat.update', params=message)

        return JsonResponse({
            'response_type': 'message',
            'text': '',
            'replace_original': True,
            'delete_original': True,
            'as_user': True,
        })

    def handle_event_rq_response(self):
        attendance_response = self.payload['actions'][0]['value']
        event_id = self.action_detail
        att_res_display = dict(Attendance.ATTENDANCE_TYPES)[attendance_response]

        # msg = get_object_or_404(InteractiveMessage, id=block_id.split('_')[-1])
        # print('message found')
        attendance = get_object_or_404(Attendance, event=event_id,
                                       player__slack_user_id=self.payload['user']['id'])
        print('attendance found')

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

        message = compose_message(self.payload['container']['channel_id'],
                                  text='Succeeded',
                                  ts=self.original_time_stamp,
                                  blocks=json.dumps(blocks))
        r = requests.post('https://slack.com/api/chat.update', params=message)
        print(r.content)

        subject = 'A player has responded'
        from_email = settings.EMAIL_HOST_USER
        message = '%s has responded to %s with the response: %s' % (attendance.player.nickname,
                                                                    attendance.event.name,
                                                                    att_res_display)
        recipients = [settings.EMAIL_DEFAULT_NOTIFICATION_ADDRESS]

        send_mail(subject, message, from_email, recipients)

        return HttpResponse(status=200)
