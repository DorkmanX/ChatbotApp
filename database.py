from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

class Database:
    def __init__(self):
        try:
            self.cluster= MongoClient(os.environ['MONGO_URI'])
            self.db=self.cluster['Chatbot']
            self.db_answers=self.db['answers']
            self.db_users_states=self.db['user_states']
            self.db_cars=self.db['cars']
            self.db_templates=self.db['templates']
            self.db_test_drives=self.db["test_drives"]
            self.db_coversation_hist=self.db["conversation_history"]
            self.cluster.server_info()
            print("Connected to database")
        except:
            print("Error cannot connect to database")
    
    def find_user_state(self,user_id):
        find_user=self.db_users_states.find_one({"user_id":user_id})
        return find_user
    def insert_user_state(self,user_template):
        self.db_users_states.insert_one(user_template)
    def replace_user_state(self,user_id,user_template):
        self.db_users_states.replace_one({"user_id":user_id}, user_template, upsert=True)
    def update_user_state(self,user_id,parameters):
        self.db_users_states.update_one({"user_id":user_id},
        {"$set": {parameters[0]:parameters[1]}})
    def find_cars(self,parameters):
        if parameters:
            search=self.db_cars.find({"typ_nadwozia":parameters[0],"typ_skrzyni":parameters[1],"paliwo":parameters[2]})
            return search
        else:
            search=self.db_cars.find()
            return search
    def find_template(self,intent):
        result=self.db_templates.find_one({"intent":intent})
        return result
    def find_text_answer(self,intent,parameter):
        if any(parameter):
            answer=self.db_answers.find_one({"intent":intent,"model":parameter[0][0]})
        else:
            answer=self.db_answers.find_one({"intent":intent})
        if answer==None:
            answer="Tego pytania nie mam jeszcze w bazie danych"
            return answer
        return answer["answer"]
    def find_quick_reply(self,intent):
        search=self.db_answers.find_one({"intent":intent})
        return search
    def add_test_drive(self,template):
        self.db_test_drives.insert_one(template)
    def save_conversation(self,user_id,template):
        query = {"user_id": user_id}
        new_conversation={"$push": {"conversation_history":template }}
        self.db_coversation_hist.update_one(query, new_conversation)
    def insert_new_conversation(self,template):
        self.db_coversation_hist.insert_one(template)