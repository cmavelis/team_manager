import json
from typing import List
import enum
from enum import Enum

from team.models import Event, Player, Attendance
from team_manager import settings


class InteractiveAction(Enum):
    event_rq_dropdowns_select = enum.auto()
    event_rq_dropdowns_send = enum.auto()
    event_rq_response = enum.auto()


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
            "block_id": InteractiveAction.event_rq_response.name + "-" + str(event.id),
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
                "block_id": InteractiveAction.event_rq_dropdowns_select.name,
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
                            } for player in Player.objects.filter(active=True).order_by('nickname')
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
                            } for event in Event.this_season.all()
                        ]
                    }
                ]
            },
            {
                "type": "actions",
                "block_id": InteractiveAction.event_rq_dropdowns_send.name,
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


def replace_blocks_in_message(original_message_blocks: List[dict], block_id: str,
                              replacement_blocks: List[dict])-> List[dict]:
    """
    :param original_message_blocks: list of block dicts for the message to be edited
    :param block_id: block id from slack
    :param replacement_blocks: list of blocks to replace the block with provided id
    :return: new message, a list of blocks
    """
    new_message = []
    for i in range(len(original_message_blocks)):
        if original_message_blocks[i]['block_id'] == block_id:
            for block in replacement_blocks:
                new_message.append(block)
        else:
            new_message.append(original_message_blocks[i])

    return new_message

