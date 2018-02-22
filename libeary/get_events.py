import json
from urllib import request
from .abe_event import ABEEvent


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
