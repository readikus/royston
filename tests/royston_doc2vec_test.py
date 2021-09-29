from datetime import datetime as dt
import json
import os
import unittest

import dateutil.relativedelta
import pytz

from royston.royston import Royston

# load json file:

# load the test data


# Move dates to a fixture, as they are reused a lot and getting more involved.
# hardcode to calculate stories relative to this time period
snapshot_test_time_options = {
    "start": dt(2019, 1, 20, 0, 0, 1, tzinfo=pytz.UTC),
    "end": dt(2019, 1, 21, 23, 59, 5, tzinfo=pytz.UTC),
}

old_test_doc_1 = {
    "id": "123",
    "body": "Random text string",
    "date": dt(2000, 1, 20, 0, 0, 1, tzinfo=pytz.UTC),
}
old_test_doc_2 = {
    "id": "456",
    "body": "Antoher random string",
    "date": dt(2000, 1, 12, 0, 0, 1, tzinfo=pytz.UTC),
}

old_valid_time_options = {
    "start": dt(2000, 1, 20, 0, 0, 1, tzinfo=pytz.UTC),
    "end": dt(2019, 1, 21, 23, 59, 5, tzinfo=pytz.UTC),
}

test_doc = {
    "id": "123",
    "body": "Random text string",
    "date": dt.now(pytz.UTC),
}
test_doc_2 = {
    "id": "456",
    "body": "Antoher random string",
    "date": dt.now(pytz.UTC),
}
no_id_test_doc = {"body": "Another random string", "date": dt.now(pytz.UTC)}
no_date_test_doc = {"id": "123", "body": "Another random string"}

subject_test_doc_1 = {
    "id": "1",
    "body": "Random text string",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}
subject_test_doc_2 = {
    "id": "2",
    "body": "I tie laces with string",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}
subject_test_doc_3 = {
    "id": "3",
    "body": "Can you string a sentence together",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}
subject_test_doc_4 = {
    "id": "4",
    "body": "My fave theory is string theory",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}
subject_test_doc_5 = {
    "id": "5",
    "body": "I live on a shoe string",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}

now = dt.now(pytz.UTC)

used_phrases = [
    ("antoher",),
    ("antoher", "random"),
    ("antoher", "random", "string"),
    ("random",),
    ("random", "string"),
    ("random", "text"),
    ("random", "text", "string"),
    ("string",),
    ("text",),
    ("text", "string"),
]

find_doc_options = {
    "start": now - dateutil.relativedelta.relativedelta(months=1),
    "end": dt.now(pytz.UTC),
}

find_doc_options_with_subject = {**find_doc_options, "subject": "wombles"}

past_history_options = {
    "start": now
    - dateutil.relativedelta.relativedelta(
        years=2
    ),  # moment().subtract(2, 'year'),
    "end": now
    - dateutil.relativedelta.relativedelta(
        years=1
    ),  # moment().subtract(1, 'year')
}


class TestRoyston(unittest.TestCase):
    def test_trending_correct_phrases(self):
        # create a model from training data
        r = Royston(snapshot_test_time_options)
        with open(
            os.path.dirname(__file__) + "/test-articles-small.json", "r"
        ) as article_file:
            article_data = article_file.read()
        articles = json.loads(article_data)
        r.ingest_all(articles)

        # @TODO: set this on a cron to rebuild, then swap out, right?
        r.train_doc2vec()

        trends = r.trending(snapshot_test_time_options)

        assert trends[0]["phrases"] == [("yeti", "sb150")]
        assert trends[0]["score"] == [1000000000.0]
        assert trends[1]["phrases"] == [("enduro", "world", "series")]
        assert trends[1]["score"] == [84075.0]


if __name__ == "__main__":
    unittest.main()
