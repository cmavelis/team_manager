import os
import json

from team.models import Event, Player, Attendance
from django.http import JsonResponse


def send_slack_event_confirm(event, player):
    message = {
        "token": os.environ["SLACK_TOKEN"],
        "channel": player.slack_user_id,
        "as_user": True,
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
