import unittest

from royston.tc_overlap_strategy import (
    OverlapStrategy,
    is_sub_phrase,
    remove_sub_phrases,
)


class TestOverlapStrategy:
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

    def test_distance(self, raw_trends):

        strat = OverlapStrategy()
        first_second = strat.distance(raw_trends[0], raw_trends[1])
        first_third = strat.distance(raw_trends[0], raw_trends[2])

        # only 1 different element
        assert first_second == 0.25
        # no different elements
        assert first_third == 1

    def test_cluster(self, raw_trends):
        strat = OverlapStrategy()
        clusters = strat.cluster(raw_trends)
        print("first", clusters[0])
        print("2nd", clusters[1])
        assert clusters[0]["phrases"] == [
            ("tour", "de", "france"),
            ("drug", "scandal"),
        ]


if __name__ == "__main__":
    unittest.main()
