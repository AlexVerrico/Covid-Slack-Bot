from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from slack import WebClient
import CovidParser.covid_parser as covid
import threading

load_dotenv()
verificationToken = os.getenv('VERIFICATION_TOKEN')
slack_web_client = WebClient(token=os.getenv("SLACK_TOKEN"))

app = Flask(__name__)

supported_data_types = ['cases', 'deaths']

messageTemplate = """
New %data_type% for %location%:
Today: %tday%
Yesterday: %yday%
Source: %source%
"""

helpTemplate = """
*Covid AU Bot*
_A simple slack bot to give you up-to-date information on covid19_

Available commands:
* /covid new cases <location>
* /covid new deaths <location>
 
Available locations:
* aus (Australia)
* usa (America)
* nsw (New South Wales)
* vic (Victoria)
* qld (Queensland)
* sa (South Australia)
* wa (Western Australia)
* tas (Tasmania)
* nt (Northern Territory)
* act (Australian Capital Territory)
"""

locationsv2 = {
    'aus': {'name': 'Australia', 'source': 'covid19data.com.au'},
    'nsw': {'name': 'New South Wales', 'source': 'covid19data.com.au'},
    'vic': {'name': 'Victoria', 'source': 'covid19data.com.au'},
    'qld': {'name': 'Queensland', 'source': 'covid19data.com.au'},
    'sa': {'name': 'South Australia', 'source': 'covid19data.com.au'},
    'wa': {'name': 'Western Australia', 'source': 'covid19data.com.au'},
    'tas': {'name': 'Tasmania', 'source': 'covid19data.com.au'},
    'nt': {'name': 'Northern Territory', 'source': 'covid19data.com.au'},
    'act': {'name': 'Australian Capital Territory', 'source': 'covid19data.com.au'},
    'usa': {'name': 'United States Of America', 'source': 'epidemic-stats.com'}
}


def handle_command(request1):
    text = request1['text'].lower()
    data = " "
    if text.startswith('help'):
        messagecontent = helpTemplate
        message = {"channel": request1['channel_id'], "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": messagecontent}}
        ]}
        slack_web_client.chat_postMessage(**message)
        return
    if text.startswith('new '):
        junk, text = text.split('new ')
        for i in supported_data_types:
            if text.startswith(i):
                if ' ' in text:
                    data_type, location = text.split(" ", 1)
                else:
                    data_type = text
                    location = 'aus'
                print("location: %s, data_type: %s" % (location, data_type))
                data = covid.new(location=location, data_type=data_type)
            else:
                pass
        if data != " ":
            pass
        else:
            data = covid.new()
            location = 'aus'
            data_type = 'cases'
    else:
        data = "Error: that isn't supported yet"
    if data != "Error: that isn't supported yet":
        messagecontent = messageTemplate.replace('%data_type%', data_type)
        messagecontent = messagecontent.replace('%tday%', data[0])
        messagecontent = messagecontent.replace('%yday%', data[1])
        if location in locationsv2:
            messagecontent = messagecontent.replace('%location%', locationsv2[location]['name'])
            messagecontent = messagecontent.replace('%source%', locationsv2[location]['source'])
        else:
            messagecontent = messagecontent.replace('%location%', location)
            messagecontent = messagecontent.replace('%source%', 'epidemic-stats.com')
    else:
        messagecontent = data
    message = {"channel": request1['channel_id'], "blocks": [
        {"type": "section", "text": {"type": "mrkdwn", "text": messagecontent}}
    ]}
    slack_web_client.chat_postMessage(**message)


@app.route('/commands/covid', methods=['POST'])
def covid_command():
    if request.form['token'] == verificationToken:
        data = request.form
        t = threading.Timer(0, handle_command, [data])
        t.start()
        payload = {'text': 'Processing...'}
        return jsonify(payload)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
