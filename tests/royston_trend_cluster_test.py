from royston.royston import Royston
from royston.trend_cluster import TrendCluster, format_d, distance, merge


class TestTrendCluster:
    def test_trending_correct_phrases(
        self, snapshot_test_time_options, small_article_data
    ):
        r = Royston(snapshot_test_time_options)
        r.ingest_all(small_article_data)
        trends = r.trending(snapshot_test_time_options)

        clusterer = TrendCluster(trends)

        print(format_d(clusterer.d))

        assert (
            format_d(clusterer.d) == "0\t0\t0\t\r\n0\t0\t0\t\r\n0\t0\t0\t\r\n"
        )

    def test_distance(self):
        assert distance(None, None) == 0
