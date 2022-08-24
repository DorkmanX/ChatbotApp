import json
import os
import requests
from database import Database

class Action_executor:

    def __init__(self):
        self.url="https://graph.facebook.com/v12.0/me/messages"
        self.database=Database()

    def send_text_message(self,user_id,message):

        payload = json.dumps({"recipient":{ "id":user_id },
            "message":{ "text":message },
            'messaging_type': 'RESPONSE' 
            })

        self.call_send_api(payload)

    def send_generic_template(self,user_id,elements_list):
   
        payload = json.dumps({"recipient":{
        "id":user_id
        },
        "message":{
        "attachment":{
        "type":"template",
        "payload":{
        "template_type":"generic",
        "elements":elements_list
        }}}})
        self.call_send_api(payload)

    def send_quick_reply(self,user_id,question,buttons_payload):
        buttons=[]
        for text in buttons_payload:
            template={
            "content_type":"text",
            "title":text,
            "payload":text
            }
            buttons.append(template)
        payload = json.dumps({
        'recipient': {'id': user_id},
        'messaging_type': 'RESPONSE',
        "message":{
        "text": question,
        "quick_replies":buttons
        }})
        self.call_send_api(payload)

    def typing_on(self,user_id):
        payload=payload = json.dumps({
        "recipient":{ "id":user_id },
        "sender_action":"typing_on"
        })
        self.call_send_api(payload)

    def mark_seen(self,user_id):
        payload=payload = json.dumps({
        "recipient":{ "id":user_id },
        "sender_action":"mark_seen"
        })
        self.call_send_api(payload)

    def call_send_api(self,payload):

        params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
        headers = {
        "Content-Type": "application/json"
        }
        r = requests.post(self.url, params=params, headers=headers, data=payload) 
    
    def sender_actions(self,user_id):
        self.mark_seen(user_id)
        self.typing_on(user_id)

    def start_new_conversation(self,user_id):
        find_user=self.database.find_user_state(user_id)
        user_template={
        "user_id":user_id,
        "context":"initial",
        "last_context":"initial",
        "curr_entity":[]
        }
        if find_user==None:
            self.database.insert_user_state(user_template)
            history_template={"user_id": user_id,
            "conversation_history":[]}
            self.database.insert_new_conversation(history_template)
        else:
            self.database.replace_user_state(user_id, user_template)
            history_template={
            "user_message":"Rozpocznij rozmowę",
            "intent":"initial",
            "intent_context":"initial",
            "user_context":"initial",
            "last_context":"initial",
            "curr_entities":[],
            "required_entities":[],
            "missing_entity":[],
            "bot_action":"welcome_message"}
            self.database.save_conversation(user_id,history_template)
        message="Witaj w naszym sklepie samochodowym."
        self.send_text_message(user_id,message)
        question="Wybierz proszę o czym chcesz porozmawiać"
        categories_list=["Godziny otwarcia","Lokalizacja","Katalog","Rekomendacja","Jazda testowa"]
        self.send_quick_reply(user_id,question,categories_list)

    def unrecognized_type(self,user_id):
        self.send_text_message(user_id,"Przykro nam ale ten chatbot obsługuje jedynie wiadomości tekstowe")
    
    def process_action(self,user_id,action,action_type,parameters):
        
        if action_type=="text":
            if any(parameters):
                answer=self.database.find_text_answer(action,parameters)
                self.send_text_message(user_id,answer)
            else:
                answer=self.database.find_text_answer(action,[])
                self.send_text_message(user_id,answer)
        if action_type=="quick_reply":
            search=self.database.find_quick_reply(action)
            buttons_list=search["buttons"]
            question=search["text"]
            self.send_quick_reply(user_id,question,buttons_list)
        if action_type=="generic_template":
            if not parameters:
                result=self.database.find_cars([])
                elements_list=[]
                for r in result:
                    payload={
                "title":r["title"],
                "image_url":r["image_url"],
                "subtitle":r["subtitle"],
                "buttons":[
                {
                "type":"postback",
                "title":"Wybierz",
                "payload":r["title"]
                }              
                ]      
                }
                    elements_list.append(payload)
                self.send_text_message(user_id,"Oto lista proponowanych samochodów")
                self.send_generic_template(user_id,elements_list)
            else:
                for entity in parameters:
                    if entity[1]=="B-NAD":
                        typ_nadwozia=entity[0]
                    elif entity[1]=="B-SKRZ":
                        typ_skrzyni=entity[0]
                    elif entity[1]=="B-SIL":
                        paliwo=entity[0]
                result=self.database.find_cars([typ_nadwozia,typ_skrzyni,paliwo])
                elements_list=[]
                for r in result:
                    payload={
                        "title":r["title"],
                        "image_url":r["image_url"],
                        "subtitle":r["subtitle"],
                        "buttons":[
                        {
                        "type":"postback",
                        "title":"Wybierz",
                        "payload":r["title"]
                        }              
                        ]      
                        }     
                    elements_list.append(payload)
                self.send_text_message(user_id,"Wybierz interesujący Cie samochodów z listy")
                self.send_generic_template(user_id,elements_list)