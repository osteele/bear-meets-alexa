import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json
from lambda_function import *
from test_fixtures import ABE_events, happening_intent

# Confident that the output should be right. Mock is getting called but
# somehow being processed incorrectly by the function.


def test_whats_happening():
    with patch('lambda_function.get_events') as mock:
        instance = mock.return_value
        instance.method.return_value = ABE_events
        result_next = handle_whats_happening_next_request(happening_intent)
        mock.assert_called_once()
        assert result_next == {'response': {'outputSpeech': {
            'text': "I found 2 events coming up on the Olin calendar in the next week. On Tuesday at 05:00 AM, there's Olin Monday . On Monday at 04:00 AM, there's Spring Break .", 'type': 'PlainText'}}, 'version': '1.0'}

        #result_on = handle_whats_happening_on_request(happening_on_intent)
        # assert result_on == {'response': {'outputSpeech': {'text': 'I found 0 events coming up on the Olin calendar in the next week.', 'type': 'PlainText'}}, 'version': '1.0'}
        # define a set return value for the mock_ABE
# 		assert handle_whats_happening_on_request(intent) == 'the result'
# 		assert handle_whats_happening_on_request(intent) == 'the result'

# @patch('lambda_function.request.Request')
#@patch('lambda_function.request.urlopen')

# Not sure why the mock is being called but not stored and processed by
# the code inside. Probably similar issue with the one above


def test_get_events():
    with patch('lambda_function.request.urlopen') as mock_events:
        instance = mock_events.return_value
        instance.method.return_value = None
        mock_events.assert_called_once()
        assert get_events(start=datetime.strptime('2018-02-20', '%Y-%m-%d'),
                          end=datetime.strptime('2018-04-20', '%Y-%m-%d')) == []

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
