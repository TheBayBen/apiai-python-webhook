#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def formatDate(date):
    year,month,day = date.split("-")
    switch (month) {
            case "01": month = " Jan ";
                     break;
            case "02": month = " Feb ";
                     break;
            case "03": month = " Mar ";
                     break;
            case "04": month = " Apr ";
                     break;
            case "05": month = " May ";
                     break;
            case "06": month = " Jun ";
                     break;
            case "07": month = " Jul ";
                     break;
            case "08": month = " Aug ";
                     break;
            case "09": month = " Sep ";
                     break;
            case "10": month = " Oct ";
                     break;
            case "11": month = " Nov ";
                     break;
            case "12": month = " Dec ";
                     break;
            default: month = "Invalid month";
                     break;
        }
    date = day + month + year
    return date

def processRequest(req):
    print ("started processing")
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    print ("yql query created")
    if yql_query is None:
        print("yqlquery is empty")
        return {}
what's the weather in paris tomorrow
give me the weather for Paris

    yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
    print(yql_url)

    result = urllib.urlopen(yql_url).read()
    print("yql result: ")
    print(result)

    data = json.loads(result)
    res = makeWebhookResult(data, req)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "') and u='c'"


def makeWebhookResult(data, req):
    estimation = 0
    result = req.get("result")
    parameters = result.get("parameters")
    datedialogflow = parameters.get("date")
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    forecast = item.get('forecast')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}
        
    # print(json.dumps(item, indent=4))
    if datedialogflow is None:
        speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
                 ", the temperature is " + condition.get('temp') + " degrees"
    else:
        datedialogflow = formatDate(datedialogflow)
        while (estimation < 10) and (datedialogflow != forecast.get(str(estimation)).get('date')):
            estimation =+1
            
        if datedialogflow == forecast.get(str(estimation)).get('date'):            
            speech = "On the " + forecast.get(str(estimation)).get('date') " in " + location.get('city') ": " + \
                     forecast.get(str(estimation)).get('date').get('text') + ", the temperature are " + \
                     forecast.get(str(estimation)).get('date').get('high') + "for the maximum and" + \
                     forecast.get(str(estimation)).get('date').get('low') + "for the minimum"

    print("Response:")
    print(speech)

    slack_message = {
        "text": speech,
        "attachments": [
            {
                "title": channel.get('title'),
                "title_link": channel.get('link'),
                "color": "#36a64f",

                "fields": [
                    {
                        "title": "Condition",
                        "value": "Temp " + condition.get('temp') +
                                 " " + units.get('temperature'),
                        "short": "false"
                    },
                    {
                        "title": "Wind",
                        "value": "Speed: " + channel.get('wind').get('speed') +
                                 ", direction: " + channel.get('wind').get('direction'),
                        "short": "true"
                    },
                    {
                        "title": "Atmosphere",
                        "value": "Humidity " + channel.get('atmosphere').get('humidity') +
                                 " pressure " + channel.get('atmosphere').get('pressure'),
                        "short": "true"
                    }
                ],

                "thumb_url": "http://l.yimg.com/a/i/us/we/52/" + condition.get('code') + ".gif"
            }
        ]
    }

    facebook_message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": channel.get('title'),
                        "image_url": "http://l.yimg.com/a/i/us/we/52/" + condition.get('code') + ".gif",
                        "subtitle": speech,
                        "buttons": [
                            {
                                "type": "web_url",
                                "url": channel.get('link'),
                                "title": "View Details"
                            }
                        ]
                    }
                ]
            }
        }
    }

    print(json.dumps(slack_message))

    return {
        "speech": speech,
        "displayText": speech,
        "data": {"slack": slack_message, "facebook": facebook_message},
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }    

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
