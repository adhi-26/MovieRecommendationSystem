import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet 

STOPWORDS = stopwords.words('english')

def remove_nonascii(text):
    clean_text = [char for char in text if ord(char)<128]
    return ''.join(clean_text)

def make_lower(text: str):
    return text.lower()

def remove_stopwords(text: str):
    clean_text = ' '.join([word for word in text.split() if word not in STOPWORDS])
    return clean_text

def lemmatization(text: str, lemma = True):
    tokenizer = RegexpTokenizer(r'[a-z]+')
    wnl = WordNetLemmatizer()
    if lemma:
        clean_text = ' '.join([wnl.lemmatize(word, wordnet.VERB) for word in tokenizer.tokenize(text)])
    else:
        clean_text = ' '.join([word for word in tokenizer.tokenize(text)])
    return clean_text

def remove_html(text):
    html_pattern = re.compile('<.*?>')
    return html_pattern.sub(r'', text)

def remove_short_long_words(text):
    text = ' '.join([word for word in text.split() if len(word)>2 and len(word)<=17])
    return text

def preprocesstext(text, lemma = True):
    text = remove_nonascii(text)
    text = make_lower(text)
    text = remove_stopwords(text)
    text = remove_html(text)
    text = lemmatization(text, lemma)
    text = remove_short_long_words(text)
    return text