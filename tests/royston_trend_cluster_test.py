from royston.royston import Royston
from royston.trend_cluster import (
    TrendCluster,
    format_d,
    distance,
    merge,
    closet_match,
)


class TestTrendCluster:
    def test_trending_correct_phrases(self, snapshot_options, data_small):
        r = Royston(snapshot_options)
        r.ingest_all(data_small)
        trends = r.trending(snapshot_options)
        clusterer = TrendCluster(trends)

        assert (
            format_d(clusterer.d) == "0\t0\t0\t\r\n0\t0\t0\t\r\n0\t0\t0\t\r\n"
        )

    def test_trending_no_data(self):
        r = Royston({})
        [trends, _] = r.trend_phrases({})
        clusterer = TrendCluster(trends)
        clusters = clusterer.cluster()
        assert clusters == []

    def test_distance(self):
        assert distance(None, None) == 0

    def test_closet_match(self):

        assert closet_match([[0]], 0.4) is None
        assert closet_match(
            [[0, 0.9, 0.3], [0.9, 0, 0.5], [0.3, 0.5, 0]], 0.4
        ) == {"i": 0, "j": 2}
        # set threshold small, as we only care about closely related items
        assert (
            closet_match([[0, 0.9, 0.9], [0.8, 0, 0.7], [0.6, 0.3, 0]], 0.2)
            is None
        )

    def merge(self):

        c_i = {"phrases": ("foo",), "score": 1, "docs": ["1", "2"]}
        c_j = {"phrases": ("bar",), "score": 2, "docs": ["2", "3", "4"]}

        c_i_and_j = merge(c_i, c_j)
        assert c_i_and_j == {
            "phrases": [("foo",), ("bar",)],
            "score": 2,
            "docs": ["1", "2", "3", "4"],
        }
