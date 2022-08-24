from nlu import NLU
from database import Database
import re

class Dialog_manager:

    
    def __init__(self):
        self.database=Database()
        self.nlu=NLU()
        
    def manager(self,user_id,messaging_text):
    
        context=self.database.find_user_state(user_id)
        action=""
        user_context= context['context']
        last_context=context['last_context']
        current_entitity_list=context['curr_entity']

        intent=self.nlu.predict_intent(messaging_text)
        extracted_entities=self.nlu.extract_ner(messaging_text)
        templates=self.database.find_template(intent)
        required_entity_list=templates["required_entity"]
        missing_entity=[]
        intent_context=templates["context"]

        if user_context=="telefon":
            if intent_context=="menu":
                user_context="menu"
            else:
                a=re.findall(r"\+?\b[\d]{3}-[\d]{3}-[\d]{3}\b", messaging_text)
                if not any(a):
                    action=["zły_numer","text",[]]
                    self.save_history(user_id,messaging_text,intent,intent_context,user_context,last_context,current_entitity_list,
                    required_entity_list,missing_entity,action)
                    return action
                else :
                    template={"user_id":user_id,"cel":"jazda testowa","samochód":current_entitity_list,"numer_telefonu":a[0]}
                    self.database.add_test_drive(template)
                    action=["jazda_umówiona","quick_reply",[]]
                    self.update_user_state(user_id,"initial","telefon",[])
                    self.save_history(user_id,messaging_text,intent,intent_context,user_context,last_context,current_entitity_list,
                    required_entity_list,missing_entity,action)
                    return action

        state_transition=False
        while state_transition==False:
            if intent=="brak_odpowiedzi":
                action=[intent,"text",[]]
                state_transition=True
            elif user_context=="initial":
                user_context=intent_context
                last_context="initial"
            elif user_context=="neutralny":
                action=[intent,"text",[]]
                user_context=last_context
                state_transition=True
            elif user_context=="błędna_odpowiedź":
                action=[intent,"text",[]]
                user_context="initial"
                last_context="błędna_odpowiedź"
                current_entitity_list=[]
                state_transition=True
            elif user_context=="menu":
                action=[intent,"quick_reply",[]]
                current_entitity_list=[]
                user_context="initial"
                last_context="menu"
                state_transition=True
            elif user_context=="katalog_aut":
                action=[intent,"generic_template",[]]
                user_context="wybór_samochodu"
                state_transition=True
            elif user_context=="wybór_samochodu":
                if self.change_context(intent_context,user_context):
                    user_context=intent_context
                    current_entitity_list=[]
                    last_context="wybór_samochodu"
                else:
                    missing_entity,current_entitity_list=self.check_missing_entity(required_entity_list,
                    extracted_entities, current_entitity_list)
                
                    if not any(missing_entity):
                        if last_context=="jazda_testowa":
                            user_context="jazda_testowa"
                        else:
                            action=["auto_informacja","quick_reply",[]]
                            user_context="pytania_techniczne"
                            state_transition=True
                    else:
                        action=[missing_entity[0],"text",[]]
                        state_transition=True
                        
            elif user_context=="pytania_techniczne":
                if intent_context=="jazda_testowa":
                    user_context=intent_context
                elif self.change_context(intent_context,user_context):
                    user_context=intent_context
                    current_entitity_list=[]
                    last_context="pytania_techniczne"
                else:
                    if any(extracted_entities):
                        for lis in extracted_entities:
                            for e in lis:
                                if e in required_entity_list:
                                    current_entitity_list=[lis]
                        action=[intent,"text",current_entitity_list]
                        state_transition=True
                    else :
                        if any(current_entitity_list):
                            action=[intent,"text",current_entitity_list]
                            state_transition=True
                        else:
                            user_context="katalog_aut"
                            last_context="pytania_techniczne"
            elif user_context=="rekomendacja":
                if self.change_context(intent_context,user_context):
                    user_context=intent_context
                    current_entitity_list=[]
                else:
                    missing_entity,current_entitity_list=self.check_missing_entity(required_entity_list,
                    extracted_entities, current_entitity_list)
                    if not any(missing_entity):
                        action=["Wyświetl rekomendowane samochody","generic_template",current_entitity_list]
                        user_context="wybór_samochodu"
                        current_entitity_list=[]
                        state_transition=True
                    else:
                        action=[missing_entity[0],"quick_reply",[]]
                        state_transition=True

            elif user_context=="jazda_testowa":
                if any(current_entitity_list):
                    action=["telefon","text",[]]
                    last_context="jazda_testowa"
                    user_context="telefon"
                    state_transition=True
                
                else:
                    missing_entity,current_entitity_list=self.check_missing_entity(required_entity_list,
                    extracted_entities, current_entitity_list)
                    
                    if not any(missing_entity):
                        action=["telefon","text",[]]
                        last_context="jazda_testowa"
                        user_context="telefon"
                        state_transition=True
                    else:
                        user_context="katalog_aut"
                        last_context="jazda_testowa"
            else:
                state_transition=True
        self.save_history(user_id,messaging_text,intent,intent_context,user_context,last_context,current_entitity_list,
        required_entity_list,missing_entity,action)
        self.update_user_state(user_id,user_context,last_context,current_entitity_list)
        return action
    
    def check_missing_entity(self,required_entity_list,extracted_entities,current_entitity_list):
        temporary_list=[]
        for lis in extracted_entities:
            if lis[1] in required_entity_list:
                current_entitity_list.append(lis)
        for lis in current_entitity_list:
            temporary_list.append(lis[1])
        a=set(required_entity_list)
        b=set(temporary_list)
        missing_entity=list(a-b)
        return missing_entity,current_entitity_list
    
    def change_context(self,intent_context,user_context):
        if intent_context!=user_context:
            return True
        else :
            return False
    
    def update_user_state(self,user_id,context,last_context,curr_entity_list):
        self.database.update_user_state(user_id,["context",context])
        self.database.update_user_state(user_id,["last_context",last_context])
        self.database.update_user_state(user_id,["curr_entity",curr_entity_list])
    
    def save_history(self,user_id,messaging_text,intent,intent_context,user_context,last_context,current_entitity_list,
    required_entity_list,missing_entity,action):
        history_template={
            "user_message":messaging_text,
            "intent":intent,
            "intent_context":intent_context,
            "user_context":user_context,
            "last_context":last_context,
            "curr_entities":current_entitity_list,
            "required_entities":required_entity_list,
            "missing_entity":missing_entity,
            "bot_action":action
        }
        self.database.save_conversation(user_id,history_template)