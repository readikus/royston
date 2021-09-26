from nltk.util import ngrams
import datetime
import dateparser
import pytz
from datetime import datetime as dt
import dateutil.relativedelta
from functools import reduce
import gensim

from royston.trend_cluster import TrendCluster
from royston.util import normalise

utc = pytz.UTC

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
    if phrase_a == None or phrase_b == None or len(phrase_a) == 0 or len(phrase_b) == 0:
        return False

    # swap phrases if a is less than b
    [a, b] = [phrase_b, phrase_a] if len(phrase_b) > len(phrase_a) else [phrase_a, phrase_b]

    # Given that b is either the same or shorter than a, b will be a sub set
    # a, so start matching  similar shorter  find where the first match.
    if not b[0] in a:
        return False

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

    # sort based on length
    trend_phrases = sorted(trend_phrases, key=lambda ngram: -len(ngram['phrases']))
    for i in range(len(trend_phrases)):
        for j in range(i + 1, len(trend_phrases)):
            if trend_phrases[i] != None and trend_phrases[j] != None and is_sub_phrase(trend_phrases[i]['phrases'], trend_phrases[j]['phrases']):
                # keep the biggest one
                trend_phrases[j] = None
    return list(filter(lambda x: x != None, trend_phrases))

class Royston:

    def __init__(self, options = {}):
        self.options = {}
        self.set_options(options)
        self.docs = {}
        # initialise the multi-dimensional ngram array storage
        self.ngrams = [ [] for _ in range(self.options['max_n'] + 1) ]
        # track the usage of the ngrams
        self.ngram_history = {}
        self.last_ingest_id = None
        self.doc2vec_docs = []
        self.doc2vec_tokens = {}

    def clean_date(self, d):
        if isinstance(d, datetime.datetime):
            return d.replace(tzinfo=pytz.UTC)
        return dateparser.parse(d).replace(tzinfo=pytz.UTC)

    def get_history_period(self, history_days = None, trend_days = None, start = None):

        if history_days == None:
            history_days = self.options['history_days']
        if trend_days == None:
            trend_days = self.options['trend_days']
        if start == None:
            start = dt.now() if 'start' not in self.options else self.options['start']

        history_end = start# - dateutil.relativedelta.relativedelta(days = trend_days)
        history_start = history_end - dateutil.relativedelta.relativedelta(days = history_days)
        return [history_start, history_end]

    # returns the date range for the trend period
    def get_trend_period(self, trend_days = None):
        if trend_days == None:
            trend_days = self.options['trend_days']
        return [dt.now() - dateutil.relativedelta.relativedelta(days = trend_days), dt.now()]

    def set_periods(self, history_days = None, trend_days = None):
        [start, end] = self.get_trend_period(trend_days)
        [history_start, history_end] = self.get_history_period(trend_days)

        self.options = {**self.options, 
            'start': self.clean_date(start),
            'end': self.clean_date(end),
            'history_start': self.clean_date(history_start),
            'history_end': self.clean_date(history_end)}

    def set_options(self, options):

        # time periods being reconfigured, but ambigious
        if 'start' in options and 'history_start' not in options and 'start' in self.options and 'history_start' in self.options:
            raise Exception('start is specified in the new options, but history_start has not been specified')

        self.options = {**DEFAULT_OPTIONS, **self.options, **options}

        # none specified - so recalculate @TODO: don't store time, if it's always to be live...
        if 'start' not in options:## and 'history_start' not in options:
            self.set_periods()

        if 'history_start' not in self.options:
            [history_start, history_end] = self.get_history_period()
            self.options = {**self.options, **{ 'history_start': self.clean_date(history_start), 'history_end': self.clean_date(history_end)}}

        """

        # @todo: make this slightly less horrific!
        # only set defaults if no start date is set.
        if not 'start' in self.options:
            self.options['end'] = dt.now()
            self.options['start'] = dt.now() - dateutil.relativedelta.relativedelta(days = self.options['trend_days'])
        # get the history window dates
        """
        # clean all dates
        #for date

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
        tokens = normalise(doc['body'])
        for n in range(1, self.options['max_n'] + 1):
            doc_ngrams = ngrams(tokens, n)
            for ngram in doc_ngrams:
                self.ingest_ngram(ngram, doc, n)

        # record the id of the last ingest document
        self.last_ingest_id = doc['id']

        self.ingest_doc2vec(tokens, doc['id'])
        self.doc2vec_tokens[doc['id']] = tokens

    def ingest_all(self, docs):
        """
        ingests a set of documents into the current Royston.
        :param {docs}: a set of documents in the format expected format
        """
        for doc in docs:
            self.ingest(doc)

    # @todo: support subjects
    def ingest_doc2vec(self, tokens, doc_id):

        # For training data, add tags 
        self.doc2vec_docs.append(gensim.models.doc2vec.TaggedDocument(tokens, [doc_id]))

    def train_doc2vec(self):
        self.doc2vec_model = gensim.models.doc2vec.Doc2Vec(vector_size=500, min_count=2, epochs=2000)
        self.doc2vec_model.build_vocab(self.doc2vec_docs)
        self.doc2vec_model.train(self.doc2vec_docs, total_examples=self.doc2vec_model.corpus_count, epochs=self.doc2vec_model.epochs)

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

    def prune(self):
        """
        Super simple method that prunes in the following conditions:

        1) before the start of the history (self.options['history_start'])
        2) the phrase was used only in the history period once
        """

        def is_in_range(occurance):
            return occurance['date'] >= self.options['history_start']

        ngrams = list(self.ngram_history.keys())
        for ngram in ngrams:
            # remove anything before the start of our considered history (i.e. stuff that is two old for us to care about)
            self.ngram_history[ngram]['occurances'] = list(filter(is_in_range, self.ngram_history[ngram]['occurances']))
            # @TODO: BUG: this needs to count number of times it happened in the past (OR cron to run only daily - but that's a bit lazy)
            if len(self.ngram_history[ngram]['occurances']) < 2:
                del self.ngram_history[ngram]

    def find_docs(self, ngram, options):
        """
        Find the documents that contain the specified ngram
        """
        # sanitise input
        options['start'] = self.clean_date(options['start'])
        options['end'] = self.clean_date(options['end'])

        # not found - return nothing
        if (not ngram in self.ngram_history):
            return []

        history = self.ngram_history[ngram]

        def matcher(doc):
            full_doc = self.docs[doc['doc_id']]
            """
            this is useful for debugging, so leaving in for now
            dates_in_range = doc['date'] >= options['start'] and doc['date'] < options['end']
            subject_match = ((not 'subject' in options) or
                    ('subject' in full_doc and options['subject'] == full_doc['subject']))
            print('dates_in_range', dates_in_range)
            print('subject_match', subject_match)
            print('options actually has a subject', 'subject' in options, options)
            """
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
        return len(self.find_docs(ngram, options))

    def count_history(self, ngram):
        return self.count(ngram, { 'start': self.options['history_start'], 'end': self.options['history_end'] })

    def count_trend_period(self, ngram):
        return self.count(ngram, { 'start': self.options['start'], 'end': self.options['end'] })

    # MERGE THIS WITH GET_NGRAM_TREND, BUT I JUST CAN'T BE FUCKED RIGHT NOW
    def get_ngram_stats (self, ngram, combined_options):
        # const trendDocs = self.findDocs(ngram, { start: self.options.start, end: self.options.end })
        trend_docs = self.find_docs(ngram, combined_options)
        trend_range_count = len(trend_docs)
        ###history_options = { }
        history_range_count = self.count(ngram, { 'start': self.options['history_start'], 'end': self.options['history_end'] })
        history_day_average = self.options['history_frequency_tolerance'] * history_range_count / self.options['history_days']

        trend_day_average = trend_range_count / combined_options['trend_days']
        history_trend_range_ratio = (trend_day_average / (0.000001 if history_range_count == 0 else history_day_average))

        change = trend_day_average - history_day_average
        change_percent = (change / (0.000001 if history_range_count == 0 else history_day_average)) * 100

        return {
            'trend_range_count': trend_range_count,
            'history_range_count': history_range_count,
            'history_day_average': history_day_average,
            'trend_day_average': trend_day_average,
            'history_trend_range_ratio': history_trend_range_ratio,
            'change_percent': change_percent,
            'change': change            
        }

    #  change start and end time to be part of options early on...
    def get_ngram_trend (self, ngram, doc_phrases, combined_options):

        """
        Does the trend analysis related to an ngram.

        this needs a proper name and explaination
        """

        # score if the phrase has trended in the last 24 hours

        # const trendDocs = self.findDocs(ngram, { start: self.options.start, end: self.options.end })
        trend_docs = self.find_docs(ngram, combined_options)
        trend_range_count = len(trend_docs)
        history_range_count = self.count(ngram, { 'start': self.options['history_start'], 'end': self.options['history_end'] })
        history_day_average = self.options['history_frequency_tolerance'] * history_range_count / self.options['history_days']

        trend_day_average = trend_range_count / combined_options['trend_days']
        history_trend_range_ratio = (trend_day_average / (0.000001 if history_range_count == 0 else history_day_average))

        trend_range_daily_average = trend_range_count / combined_options['trend_days']

        change = trend_day_average - history_day_average
        change_percent = (change / (0.000001 if history_range_count == 0 else history_day_average)) * 100

        # add in the tolerance

        # if it's above the average
        # history_day_average
        if ((trend_range_count > self.options['min_trend_freq']) and (change_percent > 0)):
            phrase = {
                'phrases': ngram,
                'score': change_percent * len(ngram), #history_trend_range_ratio * len(ngram),
                'history_range_count': history_range_count,
                'trend_range_count': trend_range_count,
                'trend_day_average': trend_day_average,
                'history_day_average': history_day_average,
                'history_trend_range_ratio': history_trend_range_ratio,
                'docs': trend_docs
            }
            set_doc_phrases(doc_phrases, trend_docs, [ngram])
            return phrase
        
        return None

    def rank_trends(self, trends, doc_phrases, top_n):

        # rank the documents in each cluster, based on the docs etc.
        for trend in trends:
            docs = []
            # for each document in that trend, count the number of phrases that match
            for doc in trend['docs']:
                # count the number of phrases from the cluster that are in that doc
                inter = set(doc_phrases[doc]).intersection(set(trend['phrases']))
                matches = len(inter)
                docs.append({ 'doc': doc, 'matches': matches })

            # sort based on the number of matches
            docs = sorted(docs, key=lambda x: x['matches'], reverse=True)
            # remove unnecessary sort data now it is sorted
            trend['docs'] = [doc['doc'] for doc in docs]

        # trim to just options.trendsTopN
        return trends[0:top_n]

    """
    Validate the trending options, setting defaults where necessary.
    @todo: this whole block is manky and needs a refactor - setup, search and cluster
    @todo: Create TrendingStrategy - this is then passed as a param for doing the trending this way.
    """
    def trending(self, options = {}):

        # if times ranges aren't specified, calcuate and stash here....
        # brittle - if 'start' is set, assumes all 4 dates are set.
        if 'start' not in options:
            self.set_periods()
        combined_options = {**self.options, **options}

        """
        This is the really manky bit of code, that needs separating into a helper
        class just for the trending
        """

        # end of setup

        # start of trending:search
        combined_options = {**self.options, **options}
        start = combined_options['start']
        end = combined_options['end']

        # find all the common phrases used in respective subject, over the past day
        # this doesn't filter by subject, but it therefore should get everything, and not be a problem?
        used_phrases = self.used_phrases(start, end)

        # duplicated data used later for sorting
        doc_phrases = {}

        # score each phrase from the trend period compared to it's historic use
        trend_phrases = list(map(lambda phrase: self.get_ngram_trend(phrase, doc_phrases, combined_options), used_phrases))

        # filter out Nones
        trend_phrases = list(filter(lambda phrase: phrase != None, trend_phrases))

        # map to ngram trends
        if trend_phrases == None or len(trend_phrases) == 0:
            return []

        # remove sub phrases (i.e. "Tour de", compared to "Tour de France")
        trend_phrases = remove_sub_phrases(trend_phrases)
        # rank results on their score
        trend_phrases = sorted(trend_phrases, key=lambda phrase: -(phrase['score']))

        self.train_doc2vec()
        # add in the tokens
        # hash all the doc tokens that we care about
        def doc2vec_distance(trend_i, trend_j):
            distances = []
            for doc_i_id in trend_i['docs']:
                doc_i_tokens = self.doc2vec_tokens[doc_i_id]
                for doc_j_id in trend_j['docs']:
                    doc_j_tokens = self.doc2vec_tokens[doc_j_id]
                    sim = self.doc2vec_model.similarity_unseen_docs(doc_i_tokens, doc_j_tokens)
                    distances.append(sim)
            return 1 - (sum(distances) / len(distances))

        # end of trending:search

        # start of trending:cluster

        # run the clustering - find the phrase that is most similar to so many
        # others (i.e. i, where sum(i) = max( sum() )
        sc = TrendCluster(trend_phrases)

        # experiment between doc2vec_distance and the old approach.
        trends = sc.cluster(doc2vec_distance)

        # substitute for clustering....
        return self.rank_trends(trends, doc_phrases, self.options['trends_top_n'])
