from datetime import datetime, timedelta
from urllib import request
import json
# changed the next import so that lambda_function needn't know the internal
# organization of the libeary package
from libeary import ABEEvent, AVSIntent


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
    # This is a developer-centered message. Consider wording aimed at the user
    # of the system.
    # Stretch: log errors for analysis as to popular unrecognized intents to
    # implement next. (Maybe AWS already has a mechanism for this?)
    return prepare_response("I didn't recognize the intent " + intent.name)


def handle_whats_happening_next_request(intent, labels=None):
    """
    This function queries ABE for events happening in the next week. It handles the "WhatsHappeningNext" request from AVS.
    :param {AVSIntent} intent: the intent from AVS
    :param {list} labels: a list of labels to filter events by
    :return {list}: the events found in the next week
    """
    # Resolve the dates to look between
    today = datetime.now()
    # timedelta is a good candidate for (1) a global, or (2) a configurable
    # global, e.g. via an environment variable. The admin documentation can
    # document configuration options, and whether they're found in the code or
    # in the enviornment.
    week_from_today = today + timedelta(weeks=1)

    # Get the events
    events = get_events(start=today, end=week_from_today, labels=labels)
    # If there is an error, consider reporting this fact to the user so they
    # don't erroneously think nothing is scheduled. (This is less critical
    # with current uses of ABE. It could be more critical if you were
    # relying on the skill to tell you, say, your next class or due date.)
    if events is None:  # Make sure there wasn't an error talking to ABE
        return prepare_abe_connectivity_problem_response()

    # Build the response
    text_res = 'I found {} events coming up on the Olin calendar in the next week.'.format(len(events))
    # In Python 3.6, you can also say f'I found #{len(events)} events…'
    for event in events:
        text_res += " {}, there's {} {}.".format(event.get_start_speech(),
                                                 event.title, 'in ' + event.location if event.location else '')

    return prepare_response(text_res)


def handle_whats_happening_on_request(intent):
    """
    This function queries ABE for events happening on a specific date. It handles the "WhatsHappeningOn" intent from AVS.
    :param {AVSIntent} intent: the intent from AVS
    :return {list}: the events found on the given date
    """
    # Convert intent date to Python date
    date = intent.slots['date'].value
    # '%Y-%m-%d' looks like it's defined by the skill. Does the skill
    # documentation give this format a name that you can use as a global
    # variable, for documentation as to where the string is coming from /
    # what it means? You could define this in libeary, to move more AWS
    # specifics there.
    date = datetime.strptime(date, '%Y-%m-%d')
    tomorrow_morning = date + timedelta(days=1)  # The end time for our query

    # Get the events
    events = get_events(start=date, end=tomorrow_morning)
    # Same as previous comment. Which suggests factoring the common code from
    # handle_whats_happening_next_request and handle_whats_happening_on_request.
    # Also (now that I see this a second time), it would make sense for
    # get_events to raise an error instead of return None, as a more
    # conventional means to signal an exception, that also forces the caller
    # to think through how to handle this case.
    if events is None:  # Make sure there wasn't an error talking to ABE
        return prepare_abe_connectivity_problem_response()

    # Build the response
    date_as_words = date.strftime('%A, %B %d')
    count = len(events)
    text_res = 'I found {} event{} on {}.'.format(
        'no' if count == 0 else count, '' if count == 1 else 's', date_as_words)
    for event in events:
        text_res += " {}, there's {} {}.".format(event.get_start_speech(),
                                                 event.title, 'in ' + event.location if event.location else '')

    return prepare_response(text_res)


def prepare_abe_connectivity_problem_response():
    """
    Generates a response to send to AVS indicating there was a problem talking to ABE.
    :return {dict}: a response to be sent back to AVS
    """
    # This is a good example of a user-oriented solution message. In an actual
    # deployment, this needs to go in a context of how to find said overlord.
    return prepare_response('There was a problem speaking to ABE. Please contact your Library Overlord.')


def get_events(start=None, end=None, labels=None):
    """
    Makes any necessary HTTP requests and does any filtering necessary to get events from ABE.
    :param {datetime} start: (optional) the first day to fetch events for
    :param {datetime} end: (optional) the last day to fetch events for
    :param {list} labels: (optional) a list of tags to filter results based on
    :return {list}: the events found
    """
    # [Not part of this goal] TODO replace by a logging command
    print('Getting events between {} and {}'.format(start, end))
    # Make an HTTP request to ABE
    request_url = 'https://abe-dev.herokuapp.com/events/'  # TODO Load this from an environment variable
    # It looks like this will do the wrong thing if one of start and end is defined and the other
    # is none, so add an assert for that, e.g.
    #    assert (start and end) or (not start and not end)
    # or the more cryptic:
    #    assert bool(start) == bool(end)
    if start and end:  # If we're searching within a specific range, add that to the GET parameters
        request_url += '?start={}&end={}'.format(format_date_url(start), format_date_url(end))

    # Put as little as possible inside a `try` block. In this case, just the
    # call to `json.loads`.
    try:
        with request.urlopen(request.Request(request_url)) as res:
            # Parse the server response TODO Error checking
            res = res.read().decode()
            if res.startswith('[]'):  # TODO Why is this necessary????
                print('Found 0 events')
                return []  # No events found
            print('Found some events:', res)
            result = json.loads(res)
    # Similarly, catch as narrow an exception as possible. As originally,
    # written, this will catch network connection errors, server errors, and
    # program errors in the block above, and disguise them all as parse errors.
    except json.JSONDecodeError as e:
        # Consider logging and then re-raising the error, so that the caller
        # receives this as an error instead of checking for None.
        print('Error parsing response from ABE')
        print(e)
        return None  # Some error talking to ABE

    # Convert the result into the format we want
    events = []
    for item in result:
        # Convert JSON into an event object
        # Use a different variable for a different value type.
        event = ABEEvent(item)
        # Filter, if necessary TODO ABE does this
        if labels:
            if event.has_labels(labels):
                events.append(event)
        else:  # Filtering not necessary
            events.append(event)
    # Can also do something like:
    #   events = [ABEEvent(event) for event in result]
    #   if labels:
    #       events = [event for event in events if event.has_labels(labels)]
    # This is a matter of taste.

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
                'type': 'PlainText',
                'text': text,
            }
        }
    }
