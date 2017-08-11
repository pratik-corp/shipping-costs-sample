#!/usr/bin/env python

import urllib
import json
import os
import requests

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/', methods=['GET'])
def homepage():
    return "You've reached the demo server."

@app.route('/run_post')
def run_post():
    url = 'https://lit-escarpment-60715.herokuapp.com/webhook'
    data = {'result': {'action': 'shipping.cost', 'parameters': { 'shipping-zone': 'Europe'}}}
    headers = {'Content-Type' : 'application/json'}

    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r.text

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print("Final Response:")
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") == "shipping.cost":
        return handleShippingRequest(req)
    elif req.get("result").get("action") == "test_intent":
        return handleTestIntentNew(req)
    elif req.get("result").get("action") == "input.unknown":
        return handleNotificationRequest(req)
    else:    
        print("result action:")
        print(req.get("result").get("action"))
        return {
            "speech": "Not an implemented action.",
            "displayText": "Not an implemented action",
            "source": "apiai-backup"
        }

def handleTestIntentNew(req):
    return {
        "data": {
            "google": {
                "systemIntent": {
                    "intent": "actions.intent.TEST_INTENT",
                    "data": {
                        "@type": "type.googleapis.com/google.actions.v2.TestIntentSpec",
                        "test_input": "hello world!"
                    }
                },
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": "should I send it to your phone?",
                                "dislaytext": "should I send it to your phone?"
                            }
                        }
                    ]
                }
            }
        },
        "source": "apiai-test_intent_new",
    }

def handleNotificationRequest(req):
    # check for notif intent in req.
    return {
        "data": {
            "google": {
                "richResponse": {
                    "items": [
                        {
                            "basicCard": {
                                "image": {
                                    "url": "http://www.petsworld.in/blog/wp-content/uploads/2014/09/cute-kittens.jpg",
                                    "accessibilityText": "cat image"
                                }
                            }
                        }
                    ]
                }
            }
        },
        "source": "apiai-notif_response",
    }
def handleTestIntent(req):
    return {
        "data": {
            "google": {
                "systemIntent": {
                    "intent": "actions.intent.OPTION",
                    "data": {
                        "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
                        "listSelect": {
                            "title": "List title",
                            "items": [
                                {
                                    "optionInfo": {
                                        "key": "cat"
                                    },
                                    "title": "cat"
                                },
                                {
                                    "optionInfo": {
                                        "key": "dog"
                                    },
                                    "title": "dog"
                                }
                            ]
                        }
                    }
                },
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": "Please select an animal.",
                                "dislaytext": "Please select an animal."
                            }
                        }
                    ]
                }
            }
        },
        "contextOut": [{"name":"animal_sound", "lifespan":2}],
        "source": "apiai-test_input",
    }

def handleShippingRequest(req):
    result = req.get("result")
    parameters = result.get("parameters")
    zone = parameters.get("shipping-zone")

    cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}

    speech = "The cost of shipping to " + zone + " is " + str(cost[zone]) + " euros."

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "contextOut": [],
        "source": "apiai-shipping"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

   # print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')
