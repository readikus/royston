import unittest
from datetime import datetime as dt
import dateutil.relativedelta
from royston.royston import Royston
from royston.royston import is_sub_phrase, remove_sub_phrases
import json
import os
import pytz
# load json file:

# load the test data


# hardcode to calculate stories relative to this time period
snapshot_test_time_options = {
  'start': dt(2019, 1, 20, 0, 0, 1, tzinfo=pytz.UTC),
  'end': dt(2019, 1, 21, 23, 59, 5, tzinfo=pytz.UTC)
}

old_test_doc_1 = { 'id': '123', 'body': 'Random text string', 'date': dt(2000, 1, 20, 0, 0, 1, tzinfo=pytz.UTC) }
old_test_doc_2 = { 'id': '456', 'body': 'Antoher random string', 'date': dt(2000, 1, 12, 0, 0, 1, tzinfo=pytz.UTC) }

old_valid_time_options = {
  'start': dt(2000, 1, 20, 0, 0, 1, tzinfo=pytz.UTC),
  'end': dt(2019, 1, 21, 23, 59, 5, tzinfo=pytz.UTC)
}

test_doc = { 'id': '123', 'body': 'Random text string', 'date': dt.now(pytz.UTC) }
test_doc_2 = { 'id': '456', 'body': 'Antoher random string', 'date': dt.now(pytz.UTC) }
no_id_test_doc = { 'body': 'Another random string', 'date': dt.now(pytz.UTC) }
no_date_test_doc = { 'id': '123', 'body': 'Another random string' }

subject_test_doc_1 = { 'id': '1', 'body': 'Random text string', 'date': dt.now(pytz.UTC), 'subject': 'wombles' }
subject_test_doc_2 = { 'id': '2', 'body': 'I tie laces with string', 'date': dt.now(pytz.UTC), 'subject': 'wombles' }
subject_test_doc_3 = { 'id': '3', 'body': 'Can you string a sentence together', 'date': dt.now(pytz.UTC), 'subject': 'wombles' }
subject_test_doc_4 = { 'id': '4', 'body': 'My fave theory is string theory', 'date': dt.now(pytz.UTC), 'subject': 'wombles' }
subject_test_doc_5 = { 'id': '5', 'body': 'I live on a shoe string', 'date': dt.now(pytz.UTC), 'subject': 'wombles' }

now = dt.now(pytz.UTC   )

used_phrases = [
  ('antoher',),
  ('antoher', 'random'),
  ('antoher','random','string'),
  ('random',),
  ('random','string'),
  ('random','text'),
  ('random','text','string'),
  ('string',),
  ('text',),
  ('text','string')]

find_doc_options = {
  'start': now - dateutil.relativedelta.relativedelta(months = 1),
  'end': dt.now(pytz.UTC)
}

find_doc_options_with_subject = {**find_doc_options, 'subject': 'wombles'}

past_history_options = {
  'start': now - dateutil.relativedelta.relativedelta(years = 2), #moment().subtract(2, 'year'),
  'end': now - dateutil.relativedelta.relativedelta(years = 1) #moment().subtract(1, 'year')
}

class TestRoyston(unittest.TestCase):

    def test_is_sub_phrase(self):
        self.assertEqual(is_sub_phrase(('a',), ('a','b')), True)
        self.assertEqual(is_sub_phrase(('a','b'), ('a',)), True)
        self.assertEqual(is_sub_phrase(('c',), ('a','b')), False)
        self.assertEqual(is_sub_phrase(('c', 'b'), ('a', 'b', 'c')), False)
        self.assertEqual(is_sub_phrase(('b', 'd'), ('a', 'b', 'c', 'd')), False)
        self.assertEqual(is_sub_phrase((), ('a','b')), False)
        self.assertEqual(is_sub_phrase(None, ('a','b')), False)
        self.assertEqual(is_sub_phrase(None, None), False)

    def test_remove_sub_phrases(self):
        self.assertEqual(remove_sub_phrases([{ 'phrases': ('enduro', 'world'), 'score': 562.5, 'history_range_count': 1, 'trend_range_count': 5, 'history_day_average': 0.017777777777777778, 'history_trend_range_ratio': 281.25, 'docs': ['16', '17', '18', '19', '20']}, {'phrases': ('world',), 'score': 281.25, 'history_range_count': 1, 'trend_range_count': 5, 'history_day_average': 0.017777777777777778, 'history_trend_range_ratio': 281.25, 'docs': ['16', '17', '18', '19', '20']}]), [{'phrases': ('enduro', 'world'), 'score': 562.5, 'history_range_count': 1, 'trend_range_count': 5, 'history_day_average': 0.017777777777777778, 'history_trend_range_ratio': 281.25, 'docs': ['16', '17', '18', '19', '20']}])
        self.assertEqual(remove_sub_phrases([{ 'phrases': ('a',)}, { 'phrases': ('a','b')}]), [{ 'phrases': ('a','b')}])
        self.assertEqual(remove_sub_phrases([{ 'phrases': ('a','b')}, { 'phrases': ('a',)}]), [{ 'phrases': ('a','b')}])
        self.assertEqual(remove_sub_phrases([{ 'phrases': ('c',)}, { 'phrases': ('a','b')}]), [{ 'phrases': ('a','b')}, { 'phrases': ('c',) }])

    def test_normalise(self):
        r = Royston()
        # normalise: normalise a string
        self.assertEqual(r.normalise('My name is Ian'), ['name', 'ian'])

    def test_constructor(self):
        r = Royston({ 'min_trend_freq': 5 })
        self.assertEqual(r.options['min_trend_freq'], 5)
        self.assertEqual(r.options['history_days'], 90)

    def test_ingest_no_date(self):
        r = Royston({ 'min_trend_freq': 5 })
        with self.assertRaises(Exception) as context:
            r.ingest(no_date_test_doc)

    def test_ingest_no_id(self):
        r = Royston({ 'min_trend_freq': 5 })
        with self.assertRaises(Exception) as context:
            r.ingest(no_id_test_doc)

    def test_clean_date(self):
        r = Royston({})
        self.assertEqual(r.clean_date('2020-01-23 01:02:03'), dt(2020, 1, 23, 1, 2, 3, tzinfo=pytz.UTC))

    def test_ingest_the_same_doc_twice(self):
        r = Royston({ 'min_trend_freq': 5 })
        self.assertEqual(r.docs, {}) #maybe wrong syntax, as needs to be based on keys??

        r.ingest(test_doc)
        self.assertEqual(r.docs, { test_doc['id']: test_doc }) #maybe wrong syntax, as needs to be based on keys??

        with self.assertRaises(Exception) as context:
            r.ingest(test_doc)

    def test_ingest_all(self):
        # Test ingest_all ingests multiple documents

        r = Royston({ 'min_trend_freq': 5 })
        self.assertEqual(r.docs, {})
        r.ingest_all([test_doc, test_doc_2])
        self.assertEqual(r.docs, { test_doc['id']: test_doc, test_doc_2['id']: test_doc_2 })

    def test_used_phrases(self):
        #Test used_phrases returns the correct phrases
        r = Royston({ 'min_trend_freq': 5 })
        r.ingest_all([test_doc, test_doc_2])
        computed_phrases = r.used_phrases(find_doc_options['start'], find_doc_options['end'])
        # not perfect just looking at first element, but...
        computed_phrases = sorted(computed_phrases, key=lambda ngram: (ngram, len(ngram)))
        self.assertEqual(computed_phrases, used_phrases)
        self.assertEqual(computed_phrases, used_phrases)

        computed_phrases = r.used_phrases(r.clean_date(find_doc_options['start']), r.clean_date(find_doc_options['end']))

        # check the date filter is working to ignore stuff out of range
        r.used_phrases(find_doc_options['start'], find_doc_options['end'])
        self.assertEqual([], r.used_phrases(past_history_options['start'], past_history_options['end']))

    def test_count(self):

        r = Royston({})
        r.ingest_all([test_doc, test_doc_2])

        # count: test the count returns the correct number
        self.assertEqual(r.count(('random',), find_doc_options), 2)
        self.assertEqual(r.count(('random', 'string'), find_doc_options), 1)
        self.assertEqual(r.count(('not', 'random', 'string'), find_doc_options), 0)

        # count: not in date range
        self.assertEqual(r.count(('random'), past_history_options), 0)

    def test_find_docs(self):

        r = Royston({})
        r.ingest_all([test_doc, test_doc_2])

        # count: test the count returns the correct number
        self.assertEqual(r.find_docs(('random',), find_doc_options), ['123', '456'])

    def test_find_docs_with_subject(self):

        r = Royston({})
        r.ingest_all([test_doc, test_doc_2, subject_test_doc_1, subject_test_doc_2, subject_test_doc_3, subject_test_doc_4, subject_test_doc_5])

        # count: test the count returns the correct number
        all_docs = r.find_docs(('string',), find_doc_options)
        subject_docs = r.find_docs(('string',), find_doc_options_with_subject)

        self.assertEqual(len(all_docs), 7)
        self.assertEqual(len(subject_docs), 5)

    def test_trending_correct_phrases(self):
        r = Royston(snapshot_test_time_options)

        with open(os.path.dirname(__file__) + '/test-articles-small.json', 'r') as article_file:
            article_data = article_file.read()

        # parse file
        articles = json.loads(article_data)

        # articles = json.load('test-articles.json')
        r.ingest_all(articles)
        trends = r.trending(snapshot_test_time_options)

        self.assertEqual(trends[0]['phrases'], [('enduro', 'world', 'series')])
        self.assertEqual(trends[0]['score'],  [168.74999999999994])
        self.assertEqual(trends[1]['phrases'], [('sb150',), ('yeti',)])
        self.assertEqual(trends[1]['score'], [56.25, 56.25])

    def test_trending_no_data(self):
        r = Royston({})
        with open(os.path.dirname(__file__) + '/test-articles-small.json', 'r') as article_file:
            article_data = article_file.read()
        # parse file
        articles = json.loads(article_data)
        # articles = json.load('test-articles.json')
        r.ingest_all(articles)
        trends = r.trending(snapshot_test_time_options)

        self.assertEqual(trends, [])

if __name__ == '__main__':
    unittest.main()
