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

## Usage

To get the events happening in the next week, simply ask any of the following:

```
Alexa, ask Bear what's happening next
Alexa, ask Bear what's happening next at Olin
Alexa, ask Bear what's happening next on the Olin calendar
```

To get events on a specific date, ask something like the following:

```
Alexa, ask Bear what's happening today
Alexa, ask Bear what's happening tomorrow
Alexa, ask Bear what's happening on Tuesday
Alexa, ask Bear what's happening on March 12th
```
