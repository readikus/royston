import unittest
import pytest

from royston.royston import Royston


class TestRoystonPrune:
    def test_prune_low_frequency(self, test_doc, test_doc_2, all_options):

        r = Royston({})
        r.ingest_all([test_doc, test_doc_2])

        assert r.find_docs(("text",), all_options) == ["123"]
        r.prune()
        # count: test the count returns the correct number
        assert r.find_docs(("text",), all_options) == []

    def test_prune_old(
        self,
        snapshot_test_time_options,
        small_article_data,
        find_doc_options_incomplete,
        all_options,
    ):

        r = Royston(snapshot_test_time_options)
        r.ingest_all(small_article_data)

        # set the options to now, with incomplete details
        with pytest.raises(Exception):
            r.set_options(find_doc_options_incomplete)

        r.set_options(all_options)
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
