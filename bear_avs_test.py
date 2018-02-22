import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json
import urllib
from libeary import format_date_url
from lambda_function import *
from test_fixtures import ABE_events, happening_intent
import pytest


def test_whats_happening():
    with patch('libeary.get_events', return_value=ABE_events) as get_events_mock:
        result_next = handle_whats_happening_next_request(happening_intent)
        get_events_mock.assert_called_once()
        assert result_next == {'response': {'outputSpeech': {
            'text': "I found 2 events coming up on the Olin calendar in the next week. On Tuesday at 05:00 AM, there's Olin Monday . On Monday at 04:00 AM, there's Spring Break .", 'type': 'PlainText'}}, 'version': '1.0'}

# Here's an alternate implementation of the previous function, that uses the
# @patch decorator instead of the patch context manager. Note that this
# definition actually overwrites the previous one.


@patch('libeary.get_events', return_value=ABE_events)
def test_whats_happening(get_events_mock):
    result_next = handle_whats_happening_next_request(happening_intent)
    get_events_mock.assert_called_once()
    assert result_next == {'response': {'outputSpeech': {
        'text': "I found 2 events coming up on the Olin calendar in the next week. On Tuesday at 05:00 AM, there's Olin Monday . On Monday at 04:00 AM, there's Spring Break .", 'type': 'PlainText'}}, 'version': '1.0'}

events_json = '''
[
    {
        "end": "2018-02-21 04:59:59",
        "id": "5a760ae1e8fb6d000a5fc365",
        "labels": [
            "academic"
        ],
        "start": "2018-02-20 05:00:00",
        "sub_events": [],
        "title": "Olin Monday"
    }
]
'''


def test_get_events():
    with patch('urllib.request.urlopen') as url_open_mock:
        decode_mock = url_open_mock.return_value.__enter__.return_value.read.return_value.decode
        start_date = datetime.strptime('2018-02-20', '%Y-%m-%d')
        end_date = datetime.strptime('2018-04-20', '%Y-%m-%d')
        decode_mock.return_value = '[]'

        # test with no start or end
        libeary.get_events(start=None, end=None)
        request, = url_open_mock.call_args[0]
        assert isinstance(request, urllib.request.Request)
        assert request.host == 'abe-dev.herokuapp.com'
        assert request.selector == '/events/'

        # test start and end
        decode_mock.reset()
        libeary.get_events(start=start_date, end=end_date)
        request, = url_open_mock.call_args[0]
        assert isinstance(request, urllib.request.Request)
        assert request.host == 'abe-dev.herokuapp.com'
        assert request.selector == '/events/?start=2018-02-20&end=2018-04-20'

        # test decoding
        decode_mock.reset()
        decode_mock.return_value = '[]'
        assert libeary.get_events(start=start_date, end=end_date) == []

        decode_mock.reset()
        decode_mock.return_value = events_json
        events = libeary.get_events(start=start_date, end=end_date)
        assert len(events) == 1
        event, = events
        assert isinstance(event, ABEEvent)
        assert event.title == 'Olin Monday'

        decode_mock.reset()
        decode_mock.return_value = '--invalid_json--'
        assert libeary.get_events(start=start_date, end=end_date) == None

    with patch('urllib.request.urlopen', side_effect=urllib.error.URLError('error')):
        with pytest.raises(urllib.error.URLError):
            libeary.get_events()

# def test_get_events():
# 	with patch('lambda_function.request.Request')as mock_events:
# 		instance = mock_events.return_value
# 		instance.method.return_value = events
# 		assert get_events(start=datetime.strptime('2018-02-20','%Y-%m-%d'),end=datetime.strptime('2018-04-20','%Y-%m-%d'))== events
    # with patch('lambda_function.request.urlopen'):

    # instance = mock_events.return_value
    # instance.method.return_value = events
    # assert get_events(start=datetime.strptime('2018-02-20','%Y-%m-%d'),end=datetime.strptime('2018-04-20','%Y-%m-%d'))== events

# Check all intent cases
# def test_lambda_handler(self):

# with patch('intent') as mock_intent:
# ...     intent = mock_intent.return_value
# 		# define a set return value for the mock_ABE
# ...     intent.method.return_value = 'WhatsHappeningNext'
# 		with patch('handle_whats_happening_next_request(intent)') as mock_intent:
# ...     	handle_whats_happening_next_request(intent) = mock
# 			assert lambda_handler() == 'the result'


# ...     intent.method.return_value = 'WhatsHappeningNext'
# ...     assert lambda_handler() == 'the result'

# ...     intent.method.return_value = 'WhatsHappeningNextFeatured'
# ...     assert lambda_handler() == 'the result'

# ...     intent.method.return_value = 'WhatsHappeningOn'

def test_format_date_url():
    assert format_date_url(datetime.strptime('2007-05-12', '%Y-%m-%d'), '%Y-%m-%d') == '2007-05-12'
    assert format_date_url(datetime.strptime('2007-05-12', '%Y-%m-%d'), '%Y-%d-%m') == '2007-12-05'
    assert format_date_url(datetime.strptime('2007-05-12', '%Y-%m-%d'), '%m-%Y-%d') == '05-2007-12'
    assert format_date_url(datetime.strptime('2007-05-12', '%Y-%m-%d'), '%m-%d-%Y') == '05-12-2007'
    assert format_date_url(datetime.strptime('2007-05-12', '%Y-%m-%d'), '%d-%Y-%m') == '12-2007-05'
    assert format_date_url(datetime.strptime('2007-05-12', '%Y-%m-%d'), '%d-%m-%Y') == '12-05-2007'


def test_prepare_response():
    assert prepare_response('There was a problem speaking to ABEEvent') == {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText', 'text': 'There was a problem speaking to ABEEvent'
            }}}
