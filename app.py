import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask,send_from_directory,request
import json
from chatbot import Chatbot
import requests
from waitress import serve
import hashlib
import hmac

app = Flask(__name__)

chatbot=Chatbot()

app.config['DOWNLOAD_FOLDER'] = "./Download"
app.add_url_rule(
    "/photo/<name>", endpoint="show_photos", build_only=True
)

@app.get('/photo/<name>')
def show_photos(name):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],name)

def send_get_started_button():

    params = {
    "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
    "Content-Type": "application/json"
    }

    payload={ 
    "get_started":{
    "payload":"Rozpocznij rozmowę"
                  }
    }
    headers = {'content-type': 'application/json'}
    
    r = requests.post("https://graph.facebook.com/v12.0/me/messenger_profile", params=params, headers=headers, data=payload) 

@app.get('/webhook')
def verify():

    if 'hub.mode' in request.args and 'hub.verify_token' in request.args and 'hub.challenge' in request.args:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge=request.args.get('hub.challenge')

        if mode == 'subscribe' and token == os.environ["APP_VERIFY_TOKEN"]:
            challenge = request.args.get('hub.challenge')
            return challenge, 200
        else:
            return 'Bad auth request',403
    else:
            return 'Bad auth request',403

@app.post('/webhook')
def listener():

    data = request.data
    body = json.loads(data.decode('utf-8'))
    payload = (
        json.dumps(body, separators=(",", ":"))
        .replace("/", "\\/")
        .replace("@", "\\u0040")
        .replace("%", "\\u0025")
        .replace("<", "\\u003C")
        .encode()
    )
    app_secret = os.environ["APP_SECRET"].encode()
    expected_signature = hmac.new(
        app_secret, payload, digestmod=hashlib.sha1
    ).hexdigest()
    signature = request.headers["x-hub-signature"][5:]

    if not hmac.compare_digest(expected_signature, signature):
        return 'Bad auth request',403
    else:
        if 'object' in body and body['object'] == 'page':
            entries = body['entry']
            chatbot.process_message(entries)
            return 'EVENT_RECEIVED', 200
        else:
            return 'ERROR_BAD_PAYLOAD', 404


if __name__ == '__main__':
    
    serve(app, host='0.0.0.0', port=5000)
