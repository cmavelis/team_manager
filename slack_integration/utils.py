import json

from team.models import Event, Player, Attendance
from django.http import JsonResponse
from team_manager import settings


def send_slack_event_confirm(event, player):
    message = {
        "token": settings.SLACK_BOT_USER_TOKEN,
        "channel": player.slack_user_id,
        "as_user": True,
        "text": "Your response is requested",
        "blocks": json.dumps([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "We don't have a response from you for *%s*-- can you make it?" % event.name
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": str(allowed_response[1]),
                            "emoji": True
                        },
                        "value": str(allowed_response[0])
                    } for allowed_response in Attendance.ATTENDANCE_TYPES
                ]
            }
        ])
    }

    return message


def give_player_event_dropdowns(user_id=1):
    message = {
        # "token": settings.SLACK_BOT_USER_TOKEN,
        # "channel": user_id,
        # "as_user": True,
        "text": "Define your query",
        "blocks": json.dumps([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please pick a player"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Players",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": player.nickname,
                                "emoji": True
                            },
                            "value": player.id
                        } for player in Player.objects.all()
                    ]
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please pick an event"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Events",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": event.name,
                                "emoji": True
                            },
                            "value": event.id
                        } for event in Event.objects.all()
                    ]
                }
            }
        ])
    }

    return message


# message = {
#         "token": os.environ["SLACK_TOKEN"],
#         "channel": player.slack_user_id,
#         "as_user": False,
#         "blocks": [
#             {
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": "We don't have a response from you for *%s*-- can you make it?" % event.name
#                 }
#             },
#             {
#                 "type": "actions",
#                 "elements": [
#                     {
#                         "type": "button",
#                         "text": {
#                             "type": "plain_text",
#                             "text": str(allowed_response),
#                             "emoji": True
#                         },
#                         "value": str(allowed_response)
#                     } for allowed_response in Attendance.ATTENDANCE_TYPES
#                 ]
#             }
#         ]
#     }
