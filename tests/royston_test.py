from datetime import datetime as dt
import unittest
import pytest
import pytz

from royston.royston import Royston, is_sub_phrase, remove_sub_phrases
from royston.util import normalise


class TestRoyston:
    def test_is_sub_phrase(self):
        assert is_sub_phrase(("a",), ("a", "b")) is True
        assert is_sub_phrase(("a", "b"), ("a",)) is True
        assert is_sub_phrase(("c",), ("a", "b")) is False
        assert is_sub_phrase(("c", "b"), ("a", "b", "c")) is False
        assert is_sub_phrase(("b", "d"), ("a", "b", "c", "d")) is False
        assert is_sub_phrase((), ("a", "b")) is False
        assert is_sub_phrase(None, ("a", "b")) is False
        assert is_sub_phrase(None, None) is False

    def test_remove_sub_phrases(self):
        assert remove_sub_phrases(
            [
                {
                    "phrases": ("enduro", "world"),
                    "score": 562.5,
                    "history_range_count": 1,
                    "trend_range_count": 5,
                    "history_day_average": 0.017777777777777778,
                    "history_trend_range_ratio": 281.25,
                    "docs": ["16", "17", "18", "19", "20"],
                },
                {
                    "phrases": ("world",),
                    "score": 281.25,
                    "history_range_count": 1,
                    "trend_range_count": 5,
                    "history_day_average": 0.017777777777777778,
                    "history_trend_range_ratio": 281.25,
                    "docs": ["16", "17", "18", "19", "20"],
                },
            ]
        ) == [
            {
                "phrases": ("enduro", "world"),
                "score": 562.5,
                "history_range_count": 1,
                "trend_range_count": 5,
                "history_day_average": 0.017777777777777778,
                "history_trend_range_ratio": 281.25,
                "docs": ["16", "17", "18", "19", "20"],
            }
        ]

        assert remove_sub_phrases(
            [{"phrases": ("a",)}, {"phrases": ("a", "b")}]
        ) == [{"phrases": ("a", "b")}]
        assert remove_sub_phrases(
            [{"phrases": ("a", "b")}, {"phrases": ("a",)}]
        ) == [{"phrases": ("a", "b")}]
        assert remove_sub_phrases(
            [{"phrases": ("c",)}, {"phrases": ("a", "b")}]
        ) == [{"phrases": ("a", "b")}, {"phrases": ("c",)}]

    def test_normalise(self):
        # normalise: normalise a string
        assert normalise("My name is Ian") == ["name", "ian"]

    def test_constructor(self):
        r = Royston({"min_trend_freq": 5})
        assert r.options["min_trend_freq"] == 5
        assert r.options["history_days"] == 90

    def test_ingest_no_date(self, no_date_test_doc):
        r = Royston({"min_trend_freq": 5})
        with pytest.raises(Exception):
            r.ingest(no_date_test_doc)

    def test_ingest_no_id(self, no_id_test_doc):
        r = Royston({"min_trend_freq": 5})
        with pytest.raises(Exception):
            r.ingest(no_id_test_doc)

    def test_clean_date(self):
        r = Royston({})
        assert r.clean_date("2020-01-23 01:02:03") == dt(
            2020, 1, 23, 1, 2, 3, tzinfo=pytz.UTC
        )

    def test_ingest_the_same_doc_twice(self, doc_1):
        r = Royston({"min_trend_freq": 5})
        assert r.docs == {}
        r.ingest(doc_1)
        assert r.docs == {
            doc_1["id"]: doc_1
        }  # maybe wrong syntax, as needs to be based on keys??

        with pytest.raises(Exception):
            r.ingest(doc_1)

    def test_ingest_all(self, doc_1, doc_2):
        # Test ingest_all ingests multiple documents

        r = Royston({"min_trend_freq": 5})
        assert r.docs == {}
        r.ingest_all([doc_1, doc_2])
        assert r.docs == {
            doc_1["id"]: doc_1,
            doc_2["id"]: doc_2,
        }

    def test_used_phrases(
        self,
        doc_1,
        doc_2,
        used_phrases,
        options,
        past_history_options,
    ):
        # Test used_phrases returns the correct phrases
        r = Royston({"min_trend_freq": 5})
        r.ingest_all([doc_1, doc_2])
        computed_phrases = r.used_phrases(options["start"], options["end"])
        # not perfect just looking at first element, but...
        computed_phrases = sorted(
            computed_phrases, key=lambda ngram: (ngram, len(ngram))
        )
        assert computed_phrases == used_phrases

        computed_phrases = r.used_phrases(
            r.clean_date(options["start"]),
            r.clean_date(options["end"]),
        )

        # check the date filter is working to ignore stuff out of range
        r.used_phrases(options["start"], options["end"])
        assert (
            r.used_phrases(
                past_history_options["start"], past_history_options["end"]
            )
            == []
        )

    def test_count(self, doc_1, doc_2, options, past_history_options):

        r = Royston({})
        r.ingest_all([doc_1, doc_2])

        # count: test the count returns the correct number
        assert r.count(("random",), options) == 2
        assert r.count(("random", "string"), options) == 1
        assert r.count(("womble", "random", "string"), options) == 0

        # count: not in date range
        assert r.count(("random"), past_history_options) == 0

    def test_find_docs(self, doc_1, doc_2, options):

        r = Royston({})
        r.ingest_all([doc_1, doc_2])

        # count: test the count returns the correct number
        assert r.find_docs(("random",), options) == ["123", "456"]

    def test_count_history(self, history_docs):

        r = Royston({})
        r.ingest_all(history_docs)

        # count: test the count returns the correct number
        assert r.count_history(("random",)) == 2

    def test_count_trend_period(self, history_docs, doc_1, doc_2):

        r = Royston({})
        r.ingest_all(history_docs + [doc_1, doc_2])

        assert r.count_trend_period(("random",)) == 2

    def test_find_docs_with_subject(
        self,
        doc_1,
        doc_2,
        subject_docs,
        options,
        options_with_subject,
    ):

        r = Royston({})
        r.ingest_all([doc_1, doc_2] + subject_docs)

        # count: test the count returns the correct number
        all_docs = r.find_docs(("string",), options)
        subject_docs = r.find_docs(("string",), options_with_subject)

        assert len(all_docs) == 7
        assert len(subject_docs) == 5

    def test_trend_phrases_correct_phrases(self, data_small, snapshot_options):

        r = Royston(snapshot_options)
        r.ingest_all(data_small)
        [trend_phrases, doc_phrases] = r.trend_phrases(snapshot_options)

        assert trend_phrases[0]["phrases"] == ("yeti", "sb150")
        assert trend_phrases[0]["score"] == 1000000000.0
        assert trend_phrases[1]["phrases"] == ("sb150",)
        assert trend_phrases[1]["score"] == 500000000.0
        assert trend_phrases[2]["phrases"] == ("enduro", "world", "series")
        assert trend_phrases[2]["score"] == 84075.0

    def test_trend_phrases_no_data(self, data_small, snapshot_options):
        r = Royston({})
        r.ingest_all(data_small)
        [trend_phrases, doc_phrases] = r.trend_phrases(snapshot_options)
        assert trend_phrases == []

    def test_trending_correct_phrases(self, data_small, snapshot_options):
        r = Royston(snapshot_options)
        r.ingest_all(data_small)
        trends = r.trending(snapshot_options)

        assert trends[0]["phrases"] == [("yeti", "sb150")]
        assert trends[0]["score"] == [1000000000.0]
        assert trends[1]["phrases"] == [("enduro", "world", "series")]
        assert trends[1]["score"] == [84075.0]

    def test_trending_no_data(self, data_small, snapshot_options):
        r = Royston({})
        r.ingest_all(data_small)
        trends = r.trending(snapshot_options)

        assert trends == []

    def test_get_history_period(self):
        r = Royston({})
        [history_start, history_end] = r.get_history_period()
        delta = (history_end - history_start).days
        assert delta == 90, f"delta = {str(delta)}"

    def test_get_trend_period(self):
        r = Royston({})
        [start, end] = r.get_trend_period()
        delta = start - end
        assert delta.seconds == 86399


if __name__ == "__main__":
    unittest.main()
