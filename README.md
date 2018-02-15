# Bear meets Amazon Alexa

The purpose of this project is to enable the Olin Library (cardboard) Bear with the mystical powers of Amazon Alexa.

## Skills

The first skill we implemented allows the bear to get the latest events from the [Amorphous Blob of Events](https://github.com/olinlibrary/abe).
It uses an AWS Lambda function (in this repository) to handle the request from the Alexa Voice Service. The Lambda
function then makes a request to ABE before formulating a response for AVS. The flow of data can be depicted like so:

![Olin Library Bear and AVS data flow](https://imgur.com/8AaYmgT.png)

## Hardware setup

We attempted to set up Alexa on a Raspberry Pi, which is what currently runs the bear's other features. However, we were
unsuccessful in doing this (kept running into refresh token errors). Thus, it currently must be run on a normal Alexa-enabled
device, such as an Echo.

## Current state

As it stands now, the skill will fetch events happening in the next week and read them out to you one at a time.
The times may or may not be correct, due to some bugs with the time zones on the frontend used for adding events.
The backend (ABE) is also not taking into account timezone offsets when handling queries, so an event starting
past 7pm EST will be interpreted by the backend as starting on the next day (12am UTC).

Though filtering by labels is implemented in the Lambda function, the AVS skill is not parsing speech for a list
of labels, so that code is currently unused and untested.

## Usage

#### Deployment

In order to get this skill running on your own, you'll need to

1) deploy the Python files in this repository to AWS Lambda
2) create an Alexa Skill to handle the queries listed below (intent names should match). The

Create an intent named `WhatsHappeningNext` with no data slots to handle the following utterances:

```
what's happening next
what's happening next at Olin
what's happening next on the Olin calendar
```

To get events on a specific date, create an intent called `WhatsHappeningOn` with a data slot called
`date`. The utterance could look something like the following:

```
what's happening on {date}
```

#### Invocation

When using the skill, speak the invocation word (we used `Bear`) followed by the utterance. For example

```
Alexa, ask Bear what's happening tomorrow
```

AVS will convert colloquial dates (e.g. "tomorrow", "next Wednesday") into date strings
before being sent to the Lambda function.