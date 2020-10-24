import unittest
from datetime import datetime as dt
import dateutil.relativedelta
from royston.royston import Royston

test_doc = { 'id': '123', 'body': 'Random text string', 'date': dt.now() }
test_doc_2 = { 'id': '456', 'body': 'Antoher random string', 'date': dt.now() }
no_id_test_doc = { 'body': 'Another random string', 'date': dt.now() }
no_date_test_doc = { 'id': '123', 'body': 'Another random string' }

now = dt.now()

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
  'end': dt.now()
}

find_doc_options_with_subject = {**find_doc_options, 'subject': 'Polar  Bears'}

past_history_options = {
  'start': now - dateutil.relativedelta.relativedelta(years = 2), #moment().subtract(2, 'year'),
  'end': now - dateutil.relativedelta.relativedelta(years = 1) #moment().subtract(1, 'year')
}

class TestRoyston(unittest.TestCase):

    def test_normalise(self):
        r = Royston()
        # normalise: normalise a string
        self.assertEqual(r.normalise('My name is Ian'), ['name', 'ian'])

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
    
    def test_constructor(self):
        r = Royston({ 'minTrendFreq': 5 })
        self.assertEqual(r.options['minTrendFreq'], 5)
        self.assertEqual(r.options['historyDays'], 90)

    def test_ingest_no_date(self):
        r = Royston({ 'minTrendFreq': 5 })
        with self.assertRaises(Exception) as context:
            r.ingest(no_date_test_doc)

    def test_ingest_no_id(self):
        r = Royston({ 'minTrendFreq': 5 })
        with self.assertRaises(Exception) as context:
            r.ingest(no_id_test_doc)

    def test_clean_date(self):
        r = Royston({})
        self.assertEqual(r.clean_date('2020-01-23 01:02:03'), dt(2020, 1, 23, 1, 2, 3))

    def test_ingest_the_same_doc_twice(self):
        r = Royston({ 'minTrendFreq': 5 })
        self.assertEqual(r.docs, {}) #maybe wrong syntax, as needs to be based on keys??

        r.ingest(test_doc)
        self.assertEqual(r.docs, { test_doc['id']: test_doc }) #maybe wrong syntax, as needs to be based on keys??

        with self.assertRaises(Exception) as context:
            r.ingest(test_doc)

    def test_ingest_all(self):
        """
        Test ingest_all ingests multiple documents
        """
        r = Royston({ 'minTrendFreq': 5 })
        self.assertEqual(r.docs, {})
        r.ingest_all([test_doc, test_doc_2])
        self.assertEqual(r.docs, { test_doc['id']: test_doc, test_doc_2['id']: test_doc_2 })

    def test_used_phrases(self):
        """
        Test used_phrases returns the correct phrases
        """
        r = Royston({ 'minTrendFreq': 5 })
        r.ingest_all([test_doc, test_doc_2])
        computed_phrases = r.used_phrases(find_doc_options['start'], find_doc_options['end'])
        # not perfect just looking at first element, but...
        computed_phrases = sorted(computed_phrases, key=lambda ngram: (ngram, len(ngram)))
        self.assertEqual(computed_phrases, used_phrases)
        self.assertEqual(computed_phrases, used_phrases)

        computed_phrases = r.used_phrases(find_doc_options['start'], find_doc_options['end'])

        # check the date filter is working to ignore stuff out of range
        r.used_phrases(find_doc_options['start'], find_doc_options['end'])
        self.assertEqual([], r.used_phrases(past_history_options['start'], past_history_options['end']))


    def test_count(self):

        r = Royston({})
        r.ingest_all([test_doc, test_doc_2])

        # count: test the count returns the correct number
        self.assertEqual(r.count(('random',), find_doc_options), 2)
        self.assertEqual(r.count(('random','string'), find_doc_options), 1)
        self.assertEqual(r.count(('not','random','string'), find_doc_options), 0)

        #count: not in date range
        self.assertEqual(r.count(('random'), past_history_options), 0)

    def test_find_docs(self):

        r = Royston({})
        r.ingest_all([test_doc, test_doc_2])

        # count: test the count returns the correct number
        self.assertEqual(r.find_docs(('random',), find_doc_options), ['123', '456'])

    def test_find_docs_with_subject(self):

        r = Royston({})
        r.ingest_all([test_doc, test_doc_2])

        # count: test the count returns the correct number
        self.assertEqual(r.find_docs(('random',), find_doc_options_with_subject), [])



if __name__ == '__main__':
    unittest.main()
