from lambda_function import ABEEvent

# All intent schema
intent = {
    "languageModel": {
        "intents": [
            {
                "name": "AMAZON.CancelIntent",
                "samples": [
                    "cancel",
                    "abort"
                ]
            },
            {
                "name": "AMAZON.HelpIntent",
                "samples": [
                    "help",
                    "help me",
                    "what can I do"
                ]
            },
            {
                "name": "AMAZON.StopIntent",
                "samples": []
            },
            {
                "name": "WhatsHappeningNext",
                "samples": [
                    "what's happening next",
                    "what's up next on the calendar",
                    "what's up next on the Olin calendar",
                    "what's happening next at Olin",
                    "what's happening soon at Olin"
                ],
                "slots": []
            },
            {
                "name": "WhatsHappeningNextFeatured",
                "samples": [
                    "what's awesome happening next",
                    "what's something awesome happening next",
                    "what's something awesome happening soon",
                    "what's something awesome happening"
                ],
                "slots": []
            },
            {
                "name": "WhatsHappeningOn",
                "samples": [
                    "what's happening {date}",
                    "what's happening on {date}",
                    "what's happening at {time}"
                ],
                "slots": [
                    {
                        "name": "date",
                        "type": "AMAZON.DATE"
                    },
                    {
                        "name": "time",
                        "type": "AMAZON.TIME"
                    }
                ]
            }
        ],
        "invocationName": "bear"
    }
}

happening_on_intent = {
    "name": "WhatsHappeningOn",
    "samples": [
            "what's happening {date}",
            "what's happening on {date}",
        "what's happening at {time}"
    ],
    "slots": [
        {
            "name": "date",
            "type": "AMAZON.DATE",
            "date": "2018-02-16"
        },
        {
            "name": "time",
            "type": "AMAZON.TIME"}
    ]
}

happening_intent = {
    "name": "WhatsHappeningNext",
    "samples": [
            "what's happening next",
            "what's up next on the calendar",
        "what's up next on the Olin calendar",
        "what's happening next at Olin",
        "what's happening soon at Olin"
    ],
    "slots": []
}

events = [
    {
        "end": "2018-02-21 04:59:59",
        "id": "5a760ae1e8fb6d000a5fc365",
        "labels": [
            "academic"
        ],
        "start": "2018-02-20 05:00:00",
        "sub_events": [],
        "title": "Olin Monday"
    },
    {
        "description": "No Olin Classes",
        "end": "2018-03-24 03:59:59",
        "id": "5a760c64e8fb6d000a5fc366",
        "labels": [
            "academic"
        ],
        "start": "2018-03-19 04:00:00",
        "sub_events": [],
        "title": "Spring Break"
    }]

# create reference AVS events
ABE_events = []
for result in events:
    result = ABEEvent(result)
    ABE_events.append(result)
#assert ABE_events == []

text_res = 'I found {} events coming up on the Olin calendar in the next week.'.format(len(ABE_events))
for event in ABE_events:
    text_res += " {}, there's {} {}.".format(event.get_start_speech(), event.title,
                                             'in ' + event.location if event.location else '')
