from datetime import datetime

from dateutil import tz


class ABEEvent:

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')

    def __init__(self, dict_data):
        self.title = dict_data['title']
        self.start = self._parse_date_time(dict_data.get('start'))
        self.end = self._parse_date_time(dict_data.get('end'))
        self.location = dict_data.get('location')
        self.all_day = dict_data.get('allDay')
        self.labels = dict_data.get('labels')

    def get_start_speech(self):
        return str(self.start.strftime('All day %A' if self.all_day else 'On %A at %I:%M %p'))

    def has_labels(self, labels, exact_match=False):
        """
        Checks to see if the event contains one or all of the specified labels.
        :param {list} labels: the labels to check the event for
        :param {boolean} exact_match: if True, the event must contain all of the specified labels, otherwise a single match is adequate
        :return {boolean}: True if the event has the given labels, False otherwise
        """
        for target_label in labels:  # For each of the filter labels
            if target_label in self.labels:  # See if the event has it
                if not exact_match:  # If we're just looking for a partial match
                    return True  # We have successfully done a partial match
            elif exact_match:  # If the label is not on the event, check if we need an exact match
                return False  # Exact match failed

        return True  # Exact match successful

    @staticmethod
    def _parse_date_time(string):
        dt = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        # Convert from UTC to Eastern
        dt.replace(tzinfo=ABEEvent.from_zone)
        return dt.astimezone(ABEEvent.to_zone)

