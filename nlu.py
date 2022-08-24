import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from matplotlib import pyplot as plt
from tensorflow.keras.models import load_model
from numpy import amax,argmax
from pickle import load

class NLU:

    def __init__(self):
        self.intents_model=load_model("./Models/lstm_classification.h5")
        self.ner_model=load_model("./Models/ner_recognition.h5")
        with open("./Models/Preprocessing" ,"rb") as file:
            self.tokenizer=load(file)

    def predict_intent(self,sentence):
        clear_sentence=self.tokenizer.preprocess_sentence(sentence)
        results = self.intents_model.predict([clear_sentence])[0]
        predictions=[[i,r] for i,r in enumerate(results)]
        predictions.sort(key=lambda x: x[1], reverse=True)
        intents_tag_list=self.tokenizer.intent_tags_list
        if predictions[0][1]<0.60:
            return_class="brak_odpowiedzi"
        else:
            return_class=intents_tag_list[predictions[0][0]]
        return return_class

    def extract_ner(self,sentence):
        vectorized_sentence=self.tokenizer.preprocess_sentence(sentence)
        results = self.ner_model.predict([vectorized_sentence])[0]
        tokens=self.tokenizer.clear_sentence(sentence)
        tokens=self.tokenizer.lemmatize(tokens)
        tokenizer_ner_tags=self.tokenizer.ner_tags_list
        tag2idx=self.tokenizer.tag2idx
        extracted_entity_list=[]
        for p,w in zip(results,tokens):
            class_probability=amax(p)
            if class_probability>0.80:
                class_name=argmax(p)
                if class_name != tag2idx["O"]:
                    extracted_entity_list.append([w,tokenizer_ner_tags[class_name]])
        return extracted_entity_list

    