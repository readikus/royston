from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import string

nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')

lemmatizer = WordNetLemmatizer() 
stop_words = set(stopwords.words('english')) 
punctuation_table = str.maketrans(dict.fromkeys(string.punctuation))

def normalise(s, verbose = True):
    """
    Text analysis stage to take some raw text and convert
    it into a format that we can ingest optimally.
    """ 
    # tokenize (i.e. split)
    words = word_tokenize(s)

    # remove stop words
    filtered_sentence = [w for w in words if not w.lower() in stop_words]
    # remove punctuation - bit wonky
    filtered_sentence = [w.translate(punctuation_table) for w in filtered_sentence]
    # remove words of 1 charater or less - not sure of this.
    filtered_sentence = list(filter(lambda w: len(w) > 1, filtered_sentence))

    tokens = []
    for word in filtered_sentence:
        tokens.append(lemmatizer.lemmatize(word).lower())
    return tokens
