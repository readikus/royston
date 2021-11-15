from royston.trend_cluster_strategy import TrendClusterStrategy
from royston.trend_cluster import TrendCluster


def is_sub_phrase(phrase_a, phrase_b):

    """
    Returns true if one phrase is a sub phrase of the other.

    @params a (Array) an array of words
    @params b (Array) another array of words
    @return boolean - whether a or b is a sub-phrase of the other.
    """

    # if either are empty, return false
    if (
        phrase_a is None
        or phrase_b is None
        or len(phrase_a) == 0
        or len(phrase_b) == 0
    ):
        return False

    # swap phrases if a is less than b
    [a, b] = (
        [phrase_b, phrase_a]
        if len(phrase_b) > len(phrase_a)
        else [phrase_a, phrase_b]
    )

    # Given that b is either the same or shorter than a, b will be a sub set
    # a, so start matching  similar shorter  find where the first match.
    if not b[0] in a:
        return False

    start = a.index(b[0])

    # it was found, and check there is space
    # Rewrite just subtract a from start .. (start + )
    if (start >= 0) and ((start + len(b)) <= len(a)):
        # check the rest matches
        for j in range(1, len(b)):
            if b[j] != a[start + j]:
                return False

        return True

    return False


def remove_sub_phrases(trend_phrases):

    # sort based on length
    trend_phrases = sorted(
        trend_phrases, key=lambda ngram: -len(ngram["phrases"])
    )
    for i in range(len(trend_phrases)):
        for j in range(i + 1, len(trend_phrases)):
            if (
                trend_phrases[i] is not None
                and trend_phrases[j] is not None
                and is_sub_phrase(
                    trend_phrases[i]["phrases"], trend_phrases[j]["phrases"]
                )
            ):
                # keep the biggest one
                trend_phrases[j] = None
    return list(filter(lambda x: x is not None, trend_phrases))


class OverlapStrategy(TrendClusterStrategy):
    def distance(self, a, b):
        matches = list(set(a["docs"]) & set(b["docs"]))
        if len(matches) == 0:
            return 1
        return 1 - (len(matches) / min(len(a["docs"]), len(b["docs"])))

    def cluster(self, trend_phrases):
        # remove sub phrases (i.e. "Tour de", compared to "Tour de France")
        trend_phrases = remove_sub_phrases(trend_phrases)
        # rank results on their score
        trend_phrases = sorted(
            trend_phrases,
            key=lambda phrase: (-phrase["score"], phrase["phrases"]),
        )

        # remove sub phrases (i.e. "Tour de", compared to "Tour de France")
        trend_phrases = remove_sub_phrases(trend_phrases)
        # rank results on their score
        trend_phrases = sorted(
            trend_phrases,
            key=lambda phrase: (-phrase["score"], phrase["phrases"]),
        )

        def overlap_distance(a, b):
            return self.distance(a, b)

        # run the clustering - find the phrase that is most similar to so many
        # others (i.e. i, where sum(i) = max( sum() )
        sc = TrendCluster(trend_phrases, {"min_distance": 0.25})
        trends = sc.cluster(overlap_distance)
        return trends
