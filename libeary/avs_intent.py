class AVSIntent:
    """
    This class stores information associated with an Alexa Voice Service intent.
    """

    def __init__(self, server_response):  # TODO Error handling
        event_type = server_response['request']['type']

        # Check if the user said "Alexa, open Bear" (or the like)
        self.is_launch_request = event_type == 'LaunchRequest'

        if not self.is_launch_request:  # The user said something more than "open Bear"
            intent = server_response['request']['intent']
            self.name = intent['name']
            self.slots = {}
            if 'slots' in intent:
                for name, slot in intent['slots'].items():
                    self.slots[name] = IntentSlot(slot)
        else:  # No intent libeary if Skill was simply opened
            # Define member variables
            self.name = None
            self.slots = None


class IntentSlot:

    def __init__(self, server_data):
        self.name = server_data.get('name')
        self.value = server_data.get('value')
        self.confirmation_status = server_data.get('confirmationStatus')
