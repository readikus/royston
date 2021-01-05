import unittest
from datetime import datetime as dt
import dateutil.relativedelta
from royston.royston import Royston
from royston.trend_cluster import distance, merge, closet_match, TrendCluster
import json
import os
import pytz


# todo:
# learn python constructs
# learn python tooling - like poetry
# learn python data types

trend_a = {
    'phrases': [('a', 'b')],
    'score': 1,
    'docs': [1, 2, 3]
}
trend_b = {
    'phrases': [('c', 'd')],
    'score': 2,
    'docs': [2, 3, 4]
}
trend_c = {
    'phrases': [('e', 'f')],
    'score': 3,
    'docs': [4, 5, 6]
}
trend_d = {
    'phrases': [('g', 'h')],
    'score': 4,
    'docs': [4, 5]
}

d = [
      [0, 0.33333333333333337, 1],
      [0.33333333333333337, 0, 0.6666666666666667],
      [1, 0.6666666666666667, 0]
]

class TestTrendCluster(unittest.TestCase):

    def test_distance(self):
        self.assertEqual(distance(trend_a, trend_b), 0.33333333333333337)
        self.assertEqual(distance(trend_b, trend_a), 0.33333333333333337)
        self.assertEqual(distance(trend_a, trend_a), 0.0)
        self.assertEqual(distance(trend_b, trend_b), 0.0)
        self.assertEqual(distance(trend_a, trend_c), 1)
        self.assertEqual(distance(trend_b, trend_c), 0.6666666666666667)
  
    def test_merge(self):
        self.assertEqual(merge(trend_a, trend_b), {
            'phrases': [('a', 'b'), ('c','d')],
            'score': 3,
            'docs': [1, 2, 3, 4]
        })
        self.assertEqual(merge(trend_a, trend_c), {
            'phrases': [('a', 'b'), ('e','f')],
            'score': 4,
            'docs': [1, 2, 3, 4, 5, 6]
        })

    def test_closet_match(self):

        self.assertEqual(closet_match(d, 0.4), { 'i': 0, 'j': 1 })
        self.assertEqual(closet_match(d, 0.2), None)

    def test_trend_cluster_constructor(self):

        tc = TrendCluster([trend_a, trend_b, trend_c])
        self.assertEqual([[0,0,0], [0,0,0], [0,0,0]], tc.d)

    def test_trend_cluster_cluster(self):

        tc = TrendCluster([trend_a, trend_b, trend_c, trend_d])
        self.assertEqual(tc.cluster(), [
            {
                'phrases': [('a', 'b')],
                'score': [1],
                'docs': [1, 2, 3]
            },
            {
                'phrases': [('c', 'd')],
                'score': [2],
                'docs': [2, 3, 4]
            },
            {
                'docs': [4, 5, 6],
                'phrases': [('e', 'f'), ('g', 'h')],
                'score': [3, 4]
            }
        ])



