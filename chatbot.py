from dialog_manager import Dialog_manager
from action_executor import Action_executor

class Chatbot:
    
    def __init__(self):
        self.action=Action_executor()
        self.dialog=Dialog_manager()

    def handleMessage(self,user_id,messaging_event):
  
            if 'text' in messaging_event:
                action=self.dialog.manager(user_id,messaging_event['text'])
                self.action.process_action(user_id,action[0],action[1],action[2])
                
            else:
                self.action.unrecognized_type(user_id)
    
    def handleButtons(self,user_id,messaging_event):

        payload=messaging_event['payload']

        if payload=="Rozpocznij rozmowę":
            self.action.start_new_conversation(user_id)
        else:
            action=self.dialog.manager(user_id,payload)
            self.action.process_action(user_id,action[0],action[1],action[2])
    
    def process_message(self,entries):

        for entry in entries:
          for messaging_event in entry["messaging"]:

            user_id = messaging_event['sender']['id']
            self.action.sender_actions(user_id)
            if 'message' in messaging_event:
              self.handleMessage(user_id, messaging_event['message'])

            elif 'postback' in messaging_event:
              self.handleButtons(user_id,messaging_event['postback'])
            else:
                print("unknown_event")
    