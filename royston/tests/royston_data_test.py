import unittest
from datetime import datetime as dt
import dateutil.relativedelta
from royston.royston import Royston

import json

# load json file:

# load the test data
snapshot_test_time_options = {
  'start': dt(2019, 4, 22, 23, 48, 5),
  'end': dt(2019, 4, 23, 23, 48, 5)
}
print('blah')
test_doc = { 'id': '123', 'body': 'Random text string', 'date': dt.now() }
test_doc_2 = { 'id': '456', 'body': 'Antoher random string', 'date': dt.now() }
no_id_test_doc = { 'body': 'Another random string', 'date': dt.now() }
no_date_test_doc = { 'id': '123', 'body': 'Another random string' }

now = dt.now()

past_history_options = {
  'start': now - dateutil.relativedelta.relativedelta(years = 2), #moment().subtract(2, 'year'),
  'end': now - dateutil.relativedelta.relativedelta(years = 1) #moment().subtract(1, 'year')
}

#const moment = require('moment')
#const fs = require('fs')
#const Ramekin = require('./ramekin')


class DataTestRoyston(unittest.TestCase):

    def test_trending_correct_phrases(self):
        print('this bit')
        r = Royston(snapshot_test_time_options)
        articles = json.load('test-articles.json')
        r.ingest_all(articles)
        trends = r.trending(snapshot_test_time_options)

        self.assertEqual(trends[0]['phrases'], [('game','throne','season','episod','recap'), ('episod','recap')])
        self.assertEqual(trends[0]['score'], [124000000, 48000000])
        self.assertEqual(trends[1]['phrases'], ['samsung,delai,galaxi,fold'])
        self.assertEqual(trends[1]['score'], [7031.25])



"""

/*
ingestNGram (ngram, doc) {
*/
test('trending: returns the correct phrases', () => {

  # test trending (options = {}) {
  r = Rpyston(snapshot_test_time_options)
  const articles = JSON.parse(fs.readFileSync(`${__dirname}/tests/test-articles.json`, 'utf8'))
  r.ingestAll(articles)
  // expect(r.usedPhrases(findDocOptions)).toEqual([])
  // r.ingestAll([ testDoc, testDoc2 ])
  const trends = r.trending(snapshot_test_time_options)

  expect(trends[0].phrases).toEqual(['game,throne,season,episod,recap', 'episod,recap'])
  expect(trends[0].score).toEqual([124000000, 48000000])
  expect(trends[1].phrases).toEqual(['samsung,delai,galaxi,fold'])
  expect(trends[1].score).toEqual([7031.25])
})

test('trending: no data', () => {
  const r = new Ramekin()
  const trends = r.trending()
  expect(trends).toEqual([])
})



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
        self.assertEqual(r.clean_date('2020-01-23 01:02:03'), dt(2020, 1, 23, 1, 2, 3))

    def test_ingest_the_same_doc_twice(self):
        r = Royston({ 'min_trend_freq': 5 })
        self.assertEqual(r.docs, {}) #maybe wrong syntax, as needs to be based on keys??

        r.ingest(test_doc)
        self.assertEqual(r.docs, { test_doc['id']: test_doc }) #maybe wrong syntax, as needs to be based on keys??

        with self.assertRaises(Exception) as context:
            r.ingest(test_doc)



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
"""
if __name__ == '__main__':
    print('name is main')
    unittest.main()
else:
    print('name is')
    print(__name__)
