import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams
import datetime
import dateparser
from datetime import datetime as dt
import dateutil.relativedelta

nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')

lemmatizer = WordNetLemmatizer() 
stop_words = set(stopwords.words('english')) 

DEFAULT_OPTIONS = {
    # a threshold for the minimum number of times a phrase has to occur
    # in a single day before it can even be considered a trend for a given subject.
    # @todo: work out a logical way of calculating this per category.
    'minTrendFreq': 3,
    # the context of the number of days to consider for the history
    'historyDays': 90,
    # the number of days over which to check for trends
    'trendDays': 1,
    # the maximum size of the n-gram window
    'maxN': 6,
    # remove stop words - why wouldn't you?!
    'keepStops': False,
    # really not sure why I added this...assume it is to handle words that just didn't get mentioned in the history period.
    'historyFrequencyTolerance': 1.6,
    # @todo: This is no longer used...(but I really think it should be)
    'similarityThreshold': 0.4,
    # the maximum number of results to return.
    'trendsTopN': 8
}

class Royston:

    def __init__(self, options = {}):
        self.set_options(options)
        self.docs = {}
        # initialise the multi-dimensional ngram array storage
        self.ngrams = [ [] for _ in range(self.options['maxN'] + 1) ]
        # track the usage of the ngrams
        self.ngram_history = {}

    def set_options(self, options):

        self.options = {**DEFAULT_OPTIONS, **options}
        # @todo: make this slightly less horrific!
        # only set defaults if no start date is set.
        if not 'start' in self.options:
            self.options['end'] = dt.now()
            self.options['start'] = dt.now() - dateutil.relativedelta.relativedelta(days = self.options['trendDays']) #moment().subtract(1, 'year')
  
        # get the history window dates
        if not 'history_start' in self.options:
            self.options['history_end'] = self.options['start']
            self.options['history_start'] = self.options['history_end'] \
                - dateutil.relativedelta.relativedelta(days = self.options['historyDays'])

    def normalise(self, s):
        """
        Text analysis stage to take some raw text and convert
        it into a format that we can ingest optimally.
        @todo: create a function to map the original text
        with the normalised version. Or try maintaining capitalisation etc.
        """
        words = word_tokenize(s)
        filtered_sentence = [w for w in words if not w.lower() in stop_words] 

        tokens = []
        for word in filtered_sentence:
            tokens.append(lemmatizer.lemmatize(word).lower())

        return tokens

    def clean_date(self, d):

        if isinstance(d, datetime.datetime):
            return d
        return dateparser.parse(d)

    def ingest_ngram(self, ngram, doc, n):
        """
        Add a new ngram into the ramekin.
        """
        # construct the storable ngram object
        self.ngrams[n].append({
            'date': doc['date'], # store this so it can be pruned when old
            'ngram': ngram,
            'subject': doc['subject'] if 'subject' in doc else None
        })
        # initialised hash element
        if not ngram in self.ngram_history:
            self.ngram_history[ngram] = { 'occurances': [] }
        self.ngram_history[ngram]['occurances'].append({ 'date': doc['date'], 'doc_id': doc['id'] })

        # @todo: add this to a queue to look for trends...this.isNGramTrending(ngram, doc);

    def ingest(self, raw_doc):
        """
        Ingest a single document into the ramekin.
   
        :param raw_doc: document to ingest, in this format:
        {
            id: <Unique ID - can be any format>,
            body: "Text",
            date: <ISO Date format string, or JavaScript date object>,
            subject: <Any object>
        }
        """
        # preprocess the date to check it's in the right format.
        if not 'date' in raw_doc:
            print('raising error for no date')
            raise Exception('No \'date\' field set for document')
        date = self.clean_date(raw_doc['date'])

        # ensure there is an id set
        if not 'id' in raw_doc:
            raise Exception('No \'id\' field set for document')

        # throw error if the document already exists in the ramekin
        if raw_doc['id'] in self.docs:
            raise Exception('Document %s has already been added.' % (raw_doc['id']))
        doc = { **raw_doc, 'date': date }
        
        # we may need to revisit what doc data we store
        self.docs[doc['id']] = doc

        # generate all the [1...n]-grams for the document
        for n in range(1, self.options['maxN'] + 1):
            doc_ngrams = ngrams(self.normalise(doc['body']), n)
            for ngram in doc_ngrams:
                self.ingest_ngram(ngram, doc, n)

    def ingest_all(self, docs):
        """
        ingests a set of documents into the current Ramekin.
        :param {docs}: a set of documents in the format expected format
        """
        [self.ingest(doc) for doc in docs]

    def used_phrases(self, start, end):
        """
        Finds the phrases used between a particular date range.
        @todo: error handling.
        @pre compute to store used phrases per day/hour
        @todo: this may be the main bottle neck - if a hashmap is created,
        it reduces the searches and just sets the value each time.
        returning just the values (or keys) would be quick??
        """
        used = set()
        for ngram in self.ngram_history:
            print(self.ngram_history[ngram])
            for occurance in self.ngram_history[ngram]['occurances']:
                if occurance['date'] >= start and occurance['date'] < end:
                    used.add(ngram)
        return list(used)
