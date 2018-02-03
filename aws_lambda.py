from datetime import datetime, timedelta
from urllib import request, parse
import json


def lambda_handler(event, context):
    """
    Entry function (called by AWS)
    :param event: :param event: a dictionary with the JSON values sent from AVS
    :param context: don't know what this is
    :return: a dictionary (to be formatted as a JSON string)
    """

    # Check to see if the Skill has just been launched (via "Alexa, open Bear")
    eventType = event['request']['type']
    if eventType == 'LaunchRequest':
        return {'version': '1.0', 'response': {
            'outputSpeech': {'type': 'PlainText', 'text': 'Welcome to ABE, the Olin calendar'}
        }}

    # Else, the Skill has been invoked with some more sophisticated intent
    intentName = event['request']['intent']['name']
    if intentName == 'WhatsHappeningNext':
        # Resolve the dates to look between
        today = datetime.now()
        weekFromToday = today + timedelta(weeks=1)
        today = today.strftime('%Y-%m-%d')
        weekFromToday = weekFromToday.strftime('%Y-%m-%d')
        # Get the event data
        req = request.Request('https://abe-dev.herokuapp.com/events/')
        with request.urlopen(req) as f:
            response = f.read().decode()
            events = json.loads(response)
            print(events)
            text_res = 'I found {} events happening in the next week.'.format(len(events))
            return {'version': '1.0', 'response': {
                'outputSpeech': {'type': 'PlainText', 'text': text_res}
            }}

    return {'version': '1.0', 'response': {
        'outputSpeech': {'type': 'PlainText', 'text': 'Default response for event type ' + eventType}
    }}
