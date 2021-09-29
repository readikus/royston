from datetime import datetime as dt
import json
import os
import unittest

import dateutil.relativedelta
import pytest
import pytz

from royston.royston import Royston

# load json file:

# load the test data

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

now = dt.now()

find_doc_options_incomplete = {
    "start": now - dateutil.relativedelta.relativedelta(months=1),
    "end": dt.now(),
}
find_doc_options = {
    **find_doc_options_incomplete,
    "history_end": find_doc_options_incomplete["start"],
    "history_start": find_doc_options_incomplete["start"]
    - dateutil.relativedelta.relativedelta(days=30),
}


class TestRoystonPrune(unittest.TestCase):
    def test_prune_low_frequency(self):

        r = Royston({})
        r.ingest_all([test_doc, test_doc_2])

        assert r.find_docs(("text",), find_doc_options) == ["123"]
        r.prune()
        # count: test the count returns the correct number
        assert r.find_docs(("text",), find_doc_options) == []

    def test_prune_old(self):

        r = Royston(snapshot_test_time_options)
        with open(
            os.path.dirname(__file__) + "/test-articles-small.json", "r"
        ) as article_file:
            article_data = article_file.read()
        articles = json.loads(article_data)
        r.ingest_all(articles)

        # set the options to now, with incomplete details
        with pytest.raises(Exception):
            r.set_options(find_doc_options_incomplete)

        r.set_options(find_doc_options)
        print(r.options)
        # check count before prune (i.e. contains old docs)
        assert r.find_docs(("enduro",), snapshot_test_time_options) == [
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
        ]
        r.prune()
        # check the old docs have been pruned out
        assert r.find_docs(("enduro",), snapshot_test_time_options) == []


if __name__ == "__main__":
    unittest.main()
