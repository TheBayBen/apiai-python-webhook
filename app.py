#!/usr/bin/env python
#dateDialogflow = formatDate(dateDialogflow)
#while (estimation < 10) and (dateDialogflow != forecast.get(str(estimation)).get('date'))
#estimation =+1         
#if dateDialogflow == forecast.get(str(estimation)).get('date'):         
#" will be " + forecast[int(estimation)]['text'] + \
#forecast[int(estimation)]['high'] + \ 
#elif dateDialogflow == forecast[int(estimation)]['date']:
#            speech = "On the " + forecast[int(estimation)]['date'] + " the weather in " + location['city'] + " will be " + forecast[int(estimation)]['text'] + \
#                     " with " + forecast[int(estimation)]['high'] + " degrees for the maximum and " + forecast[int(estimation)]['low'] + \
#                     " degrees for the minimum"
import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response
from num2words import num2words

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

def dateSpoken(date):
    day,month,year = date.split(" ")
    if month == "Jan":
        month = "of January"
    elif month == "Feb":
        month = "of February"
    elif month == "Mar":
        month = "of March"
    elif month == "Apr":
        month = "of April"
    elif month == "May":
        month = "of May"    
    elif month == "Jun":
        month = "of June"
    elif month == "Jul":
        month = "of July"
    elif month == "Aug":
        month = "of August"    
    elif month == "Sep":
        month = "of September"
    elif month == "Oct":
        month = "of October"
    elif month == "Nov":
        month = "of November"
    elif month == "Dec":
        month = "of December"
    if day == "01":
        day = "first "
    elif day == "02":
        day = "second "
    elif day == "03":
        day = "third "
    elif day == "04":
        day = "fourth "    
    elif day == "05":
        day = "fifth "
    elif day == "06":
        day = "sixth " 
    elif day == "07":
        day = "seventh "
    elif day == "08":
        day = "eighth "
    elif day == "09":
        day = "ninth "
    elif day == "10":
        day = "tenth "
    elif day == "11":
        day = "eleventh "
    elif day == "12":
        day = "twelfth "
    elif day == "13":
        day = "thirteenth "
    elif day == "14":
        day = "fourteenth "
    elif day == "15":
        day = "fifteenth "
    elif day == "16":
        day = "sixteenth "
    elif day == "17":
        day = "seventeenth "
    elif day == "18":
        day = "eighteenth "
    elif day == "19":
        day = "nineteenth "
    elif day == "20":
        day = "twentieth "
    elif day == "21":
        day = "twenty-first "
    elif day == "22":
        day = "twenty-second "
    elif day == "23":
        day = "twenty-third "
    elif day == "24":
        day = "twenty-fourth "
    elif day == "25":
        day = "twenty-fifth "
    elif day == "26":
        day = "twenty-sixth "
    elif day == "27":
        day = "twenty-seventh "
    elif day == "28":
        day = "twenty-eighth "
    elif day == "29":
        day = "twenty-ninth "
    elif day == "30":
        day = "thirtieth " 
    elif day == "31":
        day = "thirty-first " 
    return day + month

def formatDate(date):
    if not date:
        return ;
    year,month,day = date.split("-")
    if month == "01":
        month = " Jan "
    elif month == "02":
        month = " Feb "
    elif month == "03":
        month = " Mar "
    elif month == "04":
        month = " Apr "
    elif month == "05":
        month = " May "
    elif month == "06":
        month = " Jun "
    elif month == "07":
        month = " Jul "
    elif month == "08":
        month = " Aug "
    elif month == "09":
        month = " Sep "
    elif month == "10":
        month = " Oct "
    elif month == "11":
        month = " Nov "
    elif month == "12":
        month = " Dec "
    date = day + month + year
    return date

def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
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
    
    estimation = 0
    result = req.get("result")
    parameters = result.get("parameters")
    dateDialogflow = parameters.get("date")
    dateDialogflow = formatDate(dateDialogflow)
    while (estimation < 10) and (dateDialogflow != forecast[estimation]['date']) and dateDialogflow:
        estimation += 1  
    # print(json.dumps(item, indent=4))
    if estimation == 10:
        speech = "I have not any weather forecast available at the given date, please give me another date"
    elif (not dateDialogflow) or (estimation == 0):
        speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
                 ", the temperature is " + num2words(int(condition.get('temp'))) + " degree"    
    elif dateDialogflow == forecast[1]['date']:
        speech = "Tomorrow the weather in " + location['city'] + " will be " + forecast[estimation]['text'] + \
                 " with " + num2words(forecast[estimation]['high']).replace('point zero', ' ') + " degrees for the maximum and " + \
                 num2words(forecast[estimation]['low']).replace('point zero', ' ') + " degrees for the minimum"
    elif dateDialogflow == forecast[estimation]['date']:
        speech = "On the " + dateSpoken(forecast[estimation]['date']) + " the weather in " + location['city'] + " will be " + forecast[estimation]['text'] + \
                 " with " + num2words(forecast[estimation]['high']).replace('point zero', ' ') + " degrees for the maximum and " + \
                 num2words(forecast[estimation]['low']).replace('point zero', ' ') + " degrees for the minimum"
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

    print "Starting app on port %d" % port

app.run(debug=False, port=port, host='0.0.0.0')
