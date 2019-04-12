create_event = {
        "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Please enter some details for the event."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Event date:"
            },
            "accessory": {
                "type": "datepicker",
                "initial_date": "2019-04-28",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date",
                    "emoji": True
                }
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Event type:"
            },
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select an item",
                    "emoji": True
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tournament",
                            "emoji": True
                        },
                        "value": "T"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Scrimmage",
                            "emoji": True
                        },
                        "value": "S"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Other",
                            "emoji": True
                        },
                        "value": "O"
                    }
                ]
            }
        }
    ]
}

bother_message = {
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "We don't have a response from you for *EVENT*-- can you make it?"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Button",
                        "emoji": True
                    },
                    "value": "click_me_123"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Button",
                        "emoji": True
                    },
                    "value": "click_me_123"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Button",
                        "emoji": True
                    },
                    "value": "click_me_123"
                }
            ]
        }
    ]
}
