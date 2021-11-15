from royston.trend_cluster import TrendCluster, closet_match, distance, merge


class TestTrendCluster:
    def test_distance(self, trend_a, trend_b, trend_c, trend_d):
        assert distance(trend_a, trend_b) == 0.33333333333333337
        assert distance(trend_b, trend_a) == 0.33333333333333337
        assert distance(trend_a, trend_a) == 0.0
        assert distance(trend_b, trend_b) == 0.0
        assert distance(trend_a, trend_c) == 1
        assert distance(trend_b, trend_c) == 0.6666666666666667

    def test_merge(self, trend_a, trend_b, trend_c):
        assert merge(trend_a, trend_b) == {
            "phrases": [("a", "b"), ("c", "d")],
            "score": 2,
            "docs": [1, 2, 3, 4],
        }
        assert merge(trend_a, trend_c) == {
            "phrases": [("a", "b"), ("e", "f")],
            "score": 3,
            "docs": [1, 2, 3, 4, 5, 6],
        }

    def test_closet_match(self, sample_d):
        assert closet_match(sample_d, 0.4) == {"i": 0, "j": 1}
        assert closet_match(sample_d, 0.2) is None

    def test_trend_cluster_constructor(self, trend_a, trend_b, trend_c):
        tc = TrendCluster([trend_a, trend_b, trend_c])
        assert tc.d == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def test_trend_cluster_cluster(self, trend_a, trend_b, trend_c, trend_d):
        tc = TrendCluster([trend_a, trend_b, trend_c, trend_d])
        assert tc.cluster() == [
            {"phrases": [("a", "b")], "score": 1, "docs": [1, 2, 3]},
            {"phrases": [("c", "d")], "score": 2, "docs": [2, 3, 4]},
            {
                "docs": [4, 5, 6],
                "phrases": [("e", "f"), ("g", "h")],
                "score": 4,
            },
        ]
