import pytest
import unittest

from royston.royston import Royston


class TestRoystonPrune:
    def test_prune_low_frequency(self, doc_1, doc_2, all_options):

        r = Royston({})
        r.ingest_all([doc_1, doc_2])

        assert r.find_docs(("text",), all_options) == ["123"]
        r.prune()
        # count: test the count returns the correct number
        assert r.find_docs(("text",), all_options) == []

    def test_prune_old(
        self,
        snapshot_options,
        data_small,
        options,
        all_options,
    ):

        r = Royston(snapshot_options)
        r.ingest_all(data_small)

        # set the options to now, with incomplete details
        with pytest.raises(Exception):
            r.set_options(options)

        r.set_options(all_options)
        # check count before prune (i.e. contains old docs)
        assert r.find_docs(("enduro",), snapshot_options) == [
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
        ]
        r.prune()
        # check the old docs have been pruned out
        assert r.find_docs(("enduro",), snapshot_options) == []


if __name__ == "__main__":
    unittest.main()
