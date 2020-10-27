import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams
import datetime
import dateparser
from datetime import datetime as dt
import dateutil.relativedelta
from functools import reduce
import string

nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')

lemmatizer = WordNetLemmatizer() 
stop_words = set(stopwords.words('english')) 

DEFAULT_OPTIONS = {
    # a threshold for the minimum number of times a phrase has to occur
    # in a single day before it can even be considered a trend for a given subject.
    # @todo: work out a logical way of calculating this per category.
    'min_trend_freq': 4,
    # the context of the number of days to consider for the history
    'history_days': 90,
    # the number of days over which to check for trends
    'trend_days': 1,
    # the maximum size of the n-gram window
    'max_n': 6,
    # remove stop words - why wouldn't you?!
    'keep_stops': False,
    # really not sure why I added this...assume it is to handle words that just didn't get mentioned in the history period.
    'history_frequency_tolerance': 1.6,
    # @todo: This is no longer used...(but I really think it should be)
    'similarity_threshold': 0.4,
    # the maximum number of results to return.
    'trends_top_n': 8
}

DAY_IN_MS = 86400000

def set_doc_phrases(doc_phrases, docs, phrases):
    """
    helper function for populating doc_phrases, such that doc_phrases[doc] = an array of
    phrases that are trending
    """
    for doc in docs:
        if not doc in doc_phrases:
            doc_phrases[doc] = []
        doc_phrases[doc] = doc_phrases[doc] + phrases
"""
def expand_trend_data (trends, docs) {
        return trends.map(trend => {
        # load all the related docs
        const fullDocs = docs.filter(doc => trend.docs.includes(doc.id)).sort((event1, event2) => event1.date - event2.date)
        return { ...trend, fullDocs };
        });
    }
"""


# put all of these helpers in a separate file....

"""
   * Returns true if one phrase is a sub phrase of the other.
   *
   * @params a (Array) an array of words
   * @params b (Array) another array of words
   * @return boolean - whether a or b is a sub-phrase of the other.
   */"""
def is_sub_phrase(phrase_a, phrase_b):

    # if either are empty, return false
    if len(phrase_a).length == 0 or lens(phraseB) == 0:
        return false

    # swap phrases if a is less than b
    [a, b] = [phrase_b, phrase_a] if len(phrase_b) > len(phrase_a) else [phrase_a, phrase_b]

    # Given that b is either the same or shorter than a, b will be a sub set
    # a, so start matching  similar shorter  find where the first match.
    start = a.index(b[0])

    # it was found, and check there is space
    # Rewrite just subtract a from start .. (start + )
    if ((start >= 0) and ((start + len(b)) <= len(a))):
        # check the rest matches
        for j in range(1, len(b)):
            if (b[j] != a[start + j]):
               return False

        return True

    return False

def remove_sub_phrases(trend_phrases):

    """
    for i in range(len(trend_phrases):
      # (let j = i + 1; j < trend_phrases.length; j++) {
      for j in range(i + 1, len(trend_phrases)): 
        if (util.isSubPhrase(trend_phrases[i].phrase, trend_phrases[j].phrase)) {
          # keep the biggest one
          const spliceI = trend_phrases[i].length > trend_phrases[j].length ? j : i
          # remove the element from the array
          trend_phrases.splice(spliceI, 1)
          # start processing again from the element that was cut out
          i = spliceI
          j = spliceI
        }
      }
    }
    """
    return trend_phrases



class Royston:

    def __init__(self, options = {}):
        self.set_options(options)
        self.docs = {}
        # initialise the multi-dimensional ngram array storage
        self.ngrams = [ [] for _ in range(self.options['max_n'] + 1) ]
        # track the usage of the ngrams
        self.ngram_history = {}

    def set_options(self, options):

        self.options = {**DEFAULT_OPTIONS, **options}
        # @todo: make this slightly less horrific!
        # only set defaults if no start date is set.
        if not 'start' in self.options:
            self.options['end'] = dt.now()
            self.options['start'] = dt.now() - dateutil.relativedelta.relativedelta(days = self.options['trend_days']) #moment().subtract(1, 'year')
  
        # get the history window dates
        if not 'history_start' in self.options:
            self.options['history_end'] = self.options['start']
            self.options['history_start'] = self.options['history_end'] \
                - dateutil.relativedelta.relativedelta(days = self.options['history_days'])

    def normalise(self, s):
        """
        Text analysis stage to take some raw text and convert
        it into a format that we can ingest optimally.
        @todo: create a function to map the original text
        with the normalised version. Or try maintaining capitalisation etc.
        """ 
        words = word_tokenize(s)
        filtered_sentence = [w for w in words if not w.lower() in stop_words]

        table = str.maketrans('', '', string.punctuation)
        filtered_sentence = [w.translate(table) for w in filtered_sentence]
        filtered_sentence = list(filter(lambda w: len(w) > 0, filtered_sentence))

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
        #self.ngrams[n].append({
        #    'date': doc['date'], # store this so it can be pruned when old
        #    'ngram': ngram,
        #    'subject': doc['subject'] if 'subject' in doc else None
        #})
        # initialised hash element
        if not ngram in self.ngram_history:
            self.ngram_history[ngram] = { 'occurances': [] }
        self.ngram_history[ngram]['occurances'].append({ 'date': doc['date'], 'doc_id': doc['id'] })

        # @todo: add this to a queue to look for trends...this.isNGramTrending(ngram, doc);

    def ingest(self, raw_doc):
        """
        Ingest a single document into the collection.
   
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
            raise Exception('No \'date\' field set for document')
        date = self.clean_date(raw_doc['date'])

        if date < self.options['history_start']:
            return

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
        for n in range(1, self.options['max_n'] + 1):
            doc_ngrams = ngrams(self.normalise(doc['body']), n)
            for ngram in doc_ngrams:
                self.ingest_ngram(ngram, doc, n)

    def ingest_all(self, docs):
        """
        ingests a set of documents into the current Royston.
        :param {docs}: a set of documents in the format expected format
        """
        for doc in docs:
            self.ingest(doc)

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
            for occurance in self.ngram_history[ngram]['occurances']:
                if occurance['date'] >= start and occurance['date'] < end:
                    used.add(ngram)
        return list(used)

    def find_docs(self, ngram, options):
        """
        Find the documents that contain the specified ngram
        """
        if (not ngram in self.ngram_history):
            return []
        history = self.ngram_history[ngram]

        def matcher(doc):
            full_doc = self.docs[doc['doc_id']]
            return (doc['date'] >= options['start'] and doc['date'] < options['end'] and
                ((not 'subject' in options) or
                    ('subject' in full_doc and options['subject'] == full_doc['subject'])))

        history_in_range = list(filter(lambda doc: matcher(doc), history['occurances']))
        # return just the ids
        return list(map(lambda history: history['doc_id'], history_in_range))

    def count(self, ngram, options):
        """
        Count the number of times that an ngrams has occurred within the
        conditions of the options.
   
        :param ngram:
        :param options:
        :return int:
        """
        matching_docs = self.find_docs(ngram, options)
        return len(matching_docs)


    #  change start and end time to be part of options early on...
    def get_ngram_trend (self, ngram, doc_phrases, trend_range_days):
        """

        Does the trend analysis related to an ngram.

        this needs a proper name and explaination

        """

        # score if the phrase has trended in the last 24 hours

        # const trendDocs = self.findDocs(ngram, { start: self.options.start, end: self.options.end })
        trend_docs = self.find_docs(ngram, self.options)
        trend_range_count = len(trend_docs)
        ###history_options = { }
        history_range_count = self.count(ngram, { 'start': self.options['history_start'], 'end': self.options['history_end'] })
        history_day_average = self.options['history_frequency_tolerance'] * history_range_count / self.options['history_days']

        trend_day_average = trend_range_count / trend_range_days
        history_trend_range_ratio = (trend_day_average / (0.000001 if history_range_count == 0 else history_day_average))

        # add in the tolerance

        # if it's above the average
        if ((trend_range_count > self.options['min_trend_freq']) and (trend_range_count > history_day_average)):
            phrase = {
                'phrase': ngram,
                'score': history_trend_range_ratio * len(ngram),
                'history_range_count': history_range_count,
                'trend_range_count': trend_range_count,
                'history_day_average': history_day_average,
                'history_trend_range_ratio': history_trend_range_ratio,
                'docs': trend_docs
            }
            set_doc_phrases(doc_phrases, trend_docs, [ngram])
            return phrase
        
        return None
  
    """
    Validate the trending options, setting defaults where necessary.
    @todo: this whole block is manky and needs a refactor - setup, search and cluster
    """
    def trending(self, options = {}):
        """
        This is the really manky bit of code, that needs separating into a helper
        class just for the trending
        """

        # maybe make it take customer commands for timings - but in reality, it's going to be real time..
        # 
        """
        # setup
        /*
        # only set defaults if no start date is set.
        if (!options.start) {
        options.start = new Date()
        options.end = new Date()
        options.start.setDate(options.end.getDate() - 1)
        }
        # get the history window dates
        if (!options.historyStart) {
        options.historyEnd = new Date(options.start)
        options.historyStart = moment(options.historyEnd).subtract(
            self.options.historyDays, 'day').toDate()
        } */
        """

        # end of setup

        # start of trending:search
        combined_options = {**self.options, **options}
        start = combined_options['start']
        end = combined_options['end']

        # find all the common phrases used in respective subject, over the past day
        used_phrases = self.used_phrases(start, end)

        # duplicated data used later for sorting
        doc_phrases = {}
        trend_range_days = (end - start).days

        # score each phrase from the trend period compared to it's historic use
        # this is a reduce
        def filter_phrases(phrase):
            return None != self.get_ngram_trend(phrase, doc_phrases, trend_range_days)

        trend_phrases = list(filter(lambda phrase: filter_phrases(phrase), used_phrases))

        print('trend_phrases')
        print(trend_phrases)

        if trend_phrases == None:
            return []

        # remove sub phrases (i.e. "Tour de", compared to "Tour de France")
        trend_phrases = remove_sub_phrases(trend_phrases)

        # rank results - @todo: needs making nicer
        #todo: trend_phrases.sort((a, b) => ((b.score === a.score) ? b.phrase.length - a.phrase.length : b.score - a.score)
        
        return trend_phrases

        # end of trending:search

        # start of trending:cluster

        # this bit works to here!!!
"""
        # run the clustering - find the phrase that is most similar to so many
        # others (i.e. i, where sum(i) = max( sum() )
        const sc = new SimpleCluster(trend_phrases)
        const trends = sc.cluster()

        # rank the documents in each cluster, based on the docs etc.
        for (let i = 0; i < trends.length; i++) {
        const trend = trends[i]
        const docs = []

        # for each document in that trend, count the number of phrases that match
        for (let j = 0; j < trend.docs.length; j++) {
            const doc = trend.docs[j]

            /*
            let a = new Set([1,2,3]);
            let b = new Set([4,3,2]);
            let intersection = new Set(
                [...a].filter(x => b.has(x)));
            */
            # count the number of phrases from the cluster that are in that doc
            const matches = _.intersection(docPhrases[doc], trend.phrases).length
            docs.push({ doc, matches })
        }

        # sort based on the number of matches
        docs.sort((a, b) => b.matches - a.matches)
        # remove unnecessary sort data now it is sorted
        trend.docs = docs.map(doc => doc.doc)
        }

        # end of trending:cluster

        # trim to just options.trendsTopN
        if (trend_phrases.length > self.options.trendsTopN) {
        trend_phrases.splice(self.options.trendsTopN, trend_phrases.length - self.options.trendsTopN)
        }
        return trends
"""