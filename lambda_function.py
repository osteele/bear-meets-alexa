from datetime import datetime, timedelta
from urllib import request
import json
import time
from libeary.abe_event import ABEEvent
from libeary.avs_intent import AVSIntent


def lambda_handler(req, context):
    """
    Entry function (called by AWS)
    :param req: a dictionary with the JSON values sent from AVS
    :param context: don't know what this is
    :return: a dictionary (to be formatted as a JSON string)
    """

    # Convert the server request to an AVSIntent object
    intent = AVSIntent(req)

    # Check if the user just opened the Skill (without specifying any actions)
    if intent.is_launch_request:
        return prepare_response('Welcome to the ABE, the Olin calendar. How may I help you?')

    # Check if the user wants to know what's happening next
    elif intent.name == 'WhatsHappeningNext':
        return handle_whats_happening_next_request(intent)

    # Check if the user wants to know what featured events are happening next
    elif intent.name == 'WhatsHappeningNextFeatured':
        return handle_whats_happening_next_request(intent, 'featured')

    elif intent.name == 'WhatsHappeningOn':  # Look up what's happening on/at a specific day/time
        return handle_whats_happening_on_request(intent)

    # There was a problem interpreting the intent
    return prepare_response("I didn't recognize the intent " + intent.name)


def handle_whats_happening_next_request(intent, labels=None):
    # Resolve the dates to look between
    today = datetime.now()
    week_from_today = today + timedelta(weeks=1)
    # today = today.strftime('%Y-%m-%d')
    # week_from_today = week_from_today.strftime('%Y-%m-%d')
    # Get the event libeary
    events = get_events(start=today, end=week_from_today, labels=labels)
    if events is None:  # Make sure there wasn't an error talking to ABE
        return prepare_abe_connectivity_problem_response()

    text_res = 'I found {} events coming up on the Olin calendar in the next week.'.format(len(events))
    for event in events:
        text_res += " {}, there's {} {}.".format(event.get_start_speech(), event.title, 'in ' + event.location if event.location else '')

    return prepare_response(text_res)


def handle_whats_happening_on_request(intent):
    date = intent.slots['date'].value
    date = datetime.strptime(date, '%Y-%m-%d')
    tomorrow_morning = date+timedelta(days=1)
    events = get_events(start=date, end=tomorrow_morning)
    if not events:  # Make sure there wasn't an error talking to ABE
        return prepare_abe_connectivity_problem_response()

    date_as_words = date.strftime('%A, %B %d')
    count = len(events)
    text_res = 'I found {} event{} on {}.'.format('no' if count == 0 else count, '' if count == 1 else 's', date_as_words)
    for event in events:
        text_res += " {}, there's {} {}.".format(event.get_start_speech(), event.title, 'in ' + event.location if event.location else '')

    return prepare_response(text_res)


def prepare_abe_connectivity_problem_response():
    return prepare_response('There was a problem speaking to ABE. Please contact your Library Overlord.')


def get_events(start=None, end=None, labels=None):
    """
    Makes any necessary HTTP requests and does any filtering necessary to get events from ABE.
    :param {datetime} start: (optional) the first day to fetch events for
    :param {datetime} end: (optional) the last day to fetch events for
    :param {list} labels: (optional) a list of tags to filter results based on
    :return {list}: the events found
    """
    print('Getting events between {} and {}'.format(start, end))
    # Make an HTTP request to ABE
    request_url = 'https://abe-dev.herokuapp.com/events/'
    if start and end:  # If we're searching within a specific range, add that to the GET parameters
        request_url += '?start={}&end={}'.format(format_date_url(start), format_date_url(end))

    try:
        with request.urlopen(request.Request(request_url)) as res:
            # Parse the server response TODO Error checking
            res = res.read().decode()
            if res.startswith('[]'):  # Why is this necessary????
                print('Found 0 events')
                return []  # No events found
            print('Found some events:', res)
            result = json.loads(res)
    except Exception as e:
        print('Error parsing response from ABE')
        print(e)
        return None  # Some error talking to ABE

    # Convert the result into the format we want
    events = []
    for event in result:
        # Convert JSON libeary into an event object
        event = ABEEvent(event)
        # Filter, if necessary TODO ABE does this
        if labels:
            if event.has_labels(labels):
                events.append(event)
        else:  # Filtering not necessary
            events.append(event)

    return events


def format_date_url(date, fmt='%Y-%m-%d'):
    """
    Formats a date as a string for making ABE requests.
    :param {datetime} date: the date to format
    :param {str} fmt: the format to use (defaults to YYYY-MM-dd)
    :return: the date in the specified string format
    """
    return date.strftime(fmt)


def prepare_response(text):
    """
    Generates a response object to be sent to AVS.
    :param text: the text for Alexa to speak
    :return {dict}: the result to send back to AVS
    """
    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText', 'text': text
            }
        }
    }

