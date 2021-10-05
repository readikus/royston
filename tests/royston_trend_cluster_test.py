from royston.royston import Royston
from royston.trend_cluster import TrendCluster, format_d, distance, merge


class TestTrendCluster:
    def test_trending_correct_phrases(self, snapshot_options, data_small):
        r = Royston(snapshot_options)
        r.ingest_all(data_small)
        trends = r.trending(snapshot_options)

        clusterer = TrendCluster(trends)

        assert (
            format_d(clusterer.d) == "0\t0\t0\t\r\n0\t0\t0\t\r\n0\t0\t0\t\r\n"
        )

    def test_distance(self):
        assert distance(None, None) == 0
