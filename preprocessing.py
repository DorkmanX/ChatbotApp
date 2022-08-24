from simplemma import lemmatize,load_data
from numpy import array
from nltk import word_tokenize
from re import sub

class PreProcesing:

    def __init__(self):
        self.max_lenght = 20
        self.langdata=load_data('pl')
        self.custom_norm={"sedan":["sedany","sedana","sedanów","sedanowi","sedanom","sedanie"],
        "hatchback":["hatchbacki","hatchbacka","hatchbacków","hatchbakom","hatchbackowi"],
        "suv":["suvom","suvy","suva","suvów","suvom"],
        "manualna":["manualu","manualną","manualnymi","manualne","manual"],
        "automat":["automatyczną","automacie","automatyczną","automatach","automatyczna"],
        "benzyna":["benzynowy","benzynowym","benzynowego","benzynowe","benzynowa"],
        "hybryd":["hybrydowy","hybrydowego","hybrydowym","hybrydowe","hybryda","hybryd"]}
    
    def prepare_preprocessing(self,x,y,z):
        
        self.create_vocabulary(x)
        self.create_intents_tags(y)
        self.create_ner_tags(z)
        self.create_dictionary(x)
        self.create_ner_dictionary(z)
        
    
    def create_vocabulary(self,x):
        x_dataset = []
        for sentence in x:
            tokenized_sentence = self.clear_sentence(sentence)
            x_dataset.append(tokenized_sentence)

        lemmatized_vocabulary=[]
        for sentence in x_dataset:
            for word in sentence:
                for key in self.custom_norm:
                    if word in self.custom_norm[key]:
                        word=key
                lemma_word=lemmatize(word, self.langdata)
                lemmatized_vocabulary.append(lemma_word)

        lemmatized_vocabulary.append("ENDPAD")
        lemmatized_vocabulary.append("OOV")
        unique_lemma_vocabulary = sorted(list(set(lemmatized_vocabulary)))
        num_lemma_words = len(unique_lemma_vocabulary)+1
        self.lemmatized_vocabulary=unique_lemma_vocabulary
        self.lemmatized_word_number=num_lemma_words

    def create_intents_tags(self, y):
        intents_tags_list=sorted(list(set(y)))
        self.intent_tags_list = intents_tags_list
        self.number_intent_tags = len(intents_tags_list)

    def create_ner_tags(self,z):
        tags = []
        for sentence in z:
            tokenized_sentence=word_tokenize(sentence)
            for tag in tokenized_sentence:
                tags.append(tag)
        
        ner_tags_list=sorted(list(set(tags)))
        self.ner_tags_list = ner_tags_list
        self.number_ner_tags = len(ner_tags_list)
        
    def create_dictionary(self,x):
        word2idx = {w: i + 1 for i, w in enumerate(self.lemmatized_vocabulary)}
        self.word2idx=word2idx
    
    def create_ner_dictionary(self,z):
        z_dataset = []
        for sentence in z:
            tokenized_sentence = word_tokenize(sentence)
            z_dataset.append(tokenized_sentence)
        self.tag2idx= {t: i for i, t in enumerate(self.ner_tags_list)}

    def encode_and_pad(self, x):
        x_dataset = []
        for sentence in x:
            tokenized_sentence = self.clear_sentence(sentence)
            lemmatized_sentence=self.lemmatize(tokenized_sentence)
            x_dataset.append(lemmatized_sentence)
        word2idx=self.word2idx
        X = [[word2idx[w] for w in s] for s in x_dataset]
        vector=X
        
        for sentence in vector:
            iterator=len(sentence)
            while iterator < self.max_lenght:
                iterator+=1
                sentence.append(word2idx["ENDPAD"])
        return array(vector)
 
    def tag_to_bag(self, y):

        bag = []
        for tag in y:
            output_bag = [0] * self.number_intent_tags
            output_bag[self.intent_tags_list.index(tag)] = 1
            bag.append(output_bag)
        return array(bag)

    def tag_to_id(self, z):
        z_dataset = []
        for sentence in z:
            tokenized_sentence = word_tokenize(sentence)
            z_dataset.append(tokenized_sentence)
        z_tag = [[self.tag2idx[w] for w in s] for s in z_dataset]
        for sentence in z_tag:
            iterator=len(sentence)
            while iterator <self.max_lenght:
                iterator+=1
                sentence.append(self.tag2idx["O"])
        return array(z_tag)
        
    def lemmatize(self,sentence):
        new_sentence=[]
        for word in sentence:
            for key in self.custom_norm:
                if word in self.custom_norm[key]:
                    word=key
            lemma_word=lemmatize(word, self.langdata)
            new_sentence.append(lemma_word)
        return new_sentence

    def clear_sentence(self,sentence):
        clear_sentence=sub(r"[^a-z0-9-.łżźśóąęńć]+", " ", sentence.lower())
        clear_sentence=word_tokenize(clear_sentence)
        return clear_sentence

    def vectorize_sentence(self,sentence):
        vectorized_sentence=sentence
        for i in range(len(vectorized_sentence)):
            if sentence[i] not in self.lemmatized_vocabulary:
                vectorized_sentence[i]='OOV'
        vectorized_sentence=[[self.word2idx[w] for w in vectorized_sentence]]
        vector=vectorized_sentence
        
        for sentence in vector:
            iterator=len(sentence)
            while iterator < self.max_lenght:
                iterator+=1
                sentence.append(self.word2idx["ENDPAD"])
        return array(vector)

    def preprocess_sentence(self,sentence):
    
        vectorized_sentence=self.clear_sentence(sentence)
        vectorized_sentence=self.lemmatize(vectorized_sentence)
        vectorized_sentence=self.vectorize_sentence(vectorized_sentence)
        
        return vectorized_sentence