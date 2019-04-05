create_event = {
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
				"emoji": 'true'
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
				"emoji": 'true'
			},
			"options": [
				{
					"text": {
						"type": "plain_text",
						"text": "Tournament",
						"emoji": 'true'
					},
					"value": "T"
				},
				{
					"text": {
						"type": "plain_text",
						"text": "Scrimmage",
						"emoji": 'true'
					},
					"value": "S"
				},
				{
					"text": {
						"type": "plain_text",
						"text": "Other",
						"emoji": 'true'
					},
					"value": "O"
				}
			]
		}
	}
}
