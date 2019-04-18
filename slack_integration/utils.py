import json

from team.models import Event, Player, Attendance
from team_manager import settings


def send_slack_event_confirm(event, player):
    question_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "We don't have a response from you for *%s*-- can you make it?" % event.name
        }
    }

    message = {
        "token": settings.SLACK_BOT_USER_TOKEN,
        "channel": player.slack_user_id,
        "as_user": True,
        "text": "Your response is requested",
        "blocks": json.dumps([
            question_block,
            {
                "type": "actions",
                "block_id": "event_rq_response",
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

    return message, question_block


def give_player_event_dropdowns(user_id=1):
    block_id = "event_rq_dropdowns"
    message = {
        # "token": settings.SLACK_BOT_USER_TOKEN,
        # "channel": user_id,
        # "as_user": True,
        "text": "Define your query",
        "blocks": json.dumps([
            {
                "type": "section",
                "block_id": block_id + "_player",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please pick a player"
                },
                "accessory": {
                    "type": "static_select",
                    "action_id": "player_id",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Player",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": player.nickname,
                                "emoji": True
                            },
                            "value": str(player.id)
                        } for player in Player.objects.all()
                    ]
                }
            },
            {
                "type": "section",
                "block_id": block_id + "_event",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please pick an event"
                },
                "accessory": {
                    "type": "static_select",
                    "action_id": "event_id",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Event",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": event.name,
                                "emoji": True
                            },
                            "value": str(event.id)
                        } for event in Event.objects.all()
                    ]
                }
            },
            {
                "type": "actions",
                "block_id": block_id + "_send",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "send_message",
                        "text": {
                            "type": "plain_text",
                            "text": "Send request",
                            "emoji": True
                        },
                        "value": "send"
                    }
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
