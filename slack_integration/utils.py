import json

from team.models import Event, Player, Attendance
from team_manager import settings


def compose_message(channel, **kwargs):
    new_message = {
        "token": settings.SLACK_BOT_USER_TOKEN,
        "channel": channel,
    }

    for key, value in kwargs.items():
        new_message[key] = value

    return new_message


def compose_event_blocks(event):
    blocks = [
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*%s*, %s" % (event.name, event.date.strftime('%B %d %Y'))
            }
        },
        {
            "type": "actions",
            "block_id": "event_rq_response_" + str(event.id),
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": str(allowed_response[1]),
                        "emoji": True
                    },
                    "value": str(allowed_response[0])
                } for allowed_response in Attendance.ATTENDANCE_TYPES if allowed_response[0] != 'P'
            ]
        }
    ]

    return blocks


def send_slack_event_confirm(events_to_query, player):
    print(events_to_query, player)
    header_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Your response has been requested for the following events.  Can you make it?"
        }
    }

    event_blocks = [block for event in events_to_query for block in compose_event_blocks(event)]

    message = {
        "token": settings.SLACK_BOT_USER_TOKEN,
        "channel": player.slack_user_id,
        "as_user": True,
        "text": "Your response has been requested",
        "blocks": json.dumps([header_block] + event_blocks)
    }

    return message, header_block


def give_player_event_dropdowns(channel):
    block_id = "event_rq_dropdowns"
    message = {
        "token": settings.SLACK_BOT_USER_TOKEN,
        "channel": channel,
        "as_user": True,
        "text": "Define your query",
        "blocks": json.dumps([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please pick a player and an event to query."
                }
            },
            {
                "type": "actions",
                "block_id": block_id + "_select",
                "elements": [
                    {
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
                                    "text": "All pending players",
                                    "emoji": True
                                },
                                "value": "0"
                            }
                        ] + [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": player.nickname,
                                    "emoji": True
                                },
                                "value": str(player.id)
                            } for player in Player.objects.filter(active=True)
                        ]
                    },
                    {
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
                                    "text": "All pending events",
                                    "emoji": True
                                },
                                "value": "0"
                            }
                        ] + [
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
                ]
            },
            {
                "type": "actions",
                "block_id": block_id + "_send",
                "elements": [
                    {
                        "type": "button",
                        "style": "primary",
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
