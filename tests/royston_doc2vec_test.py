import unittest

from royston.royston import Royston


class TestRoyston:
    def test_trending_correct_phrases(
        self, snapshot_options, data_small
    ):
        r = Royston(snapshot_options)
        r.ingest_all(data_small)
        r.train_doc2vec()

        trends = r.trending(snapshot_options)

        assert trends[0]["phrases"] == [("yeti", "sb150")]
        assert trends[0]["score"] == [1000000000.0]
        assert trends[1]["phrases"] == [("enduro", "world", "series")]
        assert trends[1]["score"] == [84075.0]


if __name__ == "__main__":
    unittest.main()
