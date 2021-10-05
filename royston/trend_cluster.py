"""
Simple clustering algorithm.
"""

DEFAULT_OPTIONS = {
    # the minimum distance
    "min_distance": 0.1973
}


# switch docs to a set instead of list
# create an interface that other algos have to implement
def format_d(d):
    s = ""
    for i in range(len(d)):
        for j in range(len(d)):
            s += str(d[i][j]) + "\t"
        s += "\r\n"
    return s


def distance(a, b):
    if a is None or b is None:
        return 0
    # replace with Sets
    matches = list(set(a["docs"]) & set(b["docs"]))
    if len(matches) == 0:
        return 1
    return 1 - (len(matches) / min(len(a["docs"]), len(b["docs"])))


def merge(i, j):
    return {
        **i,
        "phrases": i["phrases"] + j["phrases"],
        # this is nonsense - needs to rescore!
        "score": i["score"] + j["score"],
        # merge docs & remove duplicates
        "docs": list(set(i["docs"]) | set(j["docs"])),
    }


# find most match row, then match all those elements within
# a certain similarity
def closet_match(d, threshold):
    # nothing left to cluster -> everything has already clustered
    if len(d) == 1:
        return None
    # @todo: add validation.
    min = {"i": 0, "j": 1}  # point to the first non symetrical match
    # find the closest matches
    for i in range(len(d)):
        for j in range(i + 1, len(d)):
            if (i != j) and (d[i][j] < d[min["i"]][min["j"]]):
                min["i"] = i
                min["j"] = j
    if d[min["i"]][min["j"]] > threshold:
        return None

    return min


# No major reason this should stay in a class.
# Or maybe people need to implement an interface
class TrendCluster:
    def __init__(self, trend_phrases, options={}):

        self.options = {**DEFAULT_OPTIONS, **options}

        if len(trend_phrases) == 0:
            # print('No phrases to cluster')
            return

        def map_trend_to_cluster(phrase):
            return {
                "phrases": phrase["phrases"]
                if isinstance(phrase["phrases"], list)
                else [phrase["phrases"]],
                "docs": phrase["docs"],
                "score": [phrase["score"]],
            }

        # create initial clusters & populate the distance matrix
        self.c = list(map(map_trend_to_cluster, trend_phrases))
        self.d = [
            [0 for i in range(len(trend_phrases))]
            for j in range(len(trend_phrases))
        ]

    def hierachical_cluster(
        self, distance, merge, closet_match, c, d, min_distance
    ):

        # calculate the initial distance matrix
        # this can be a function, surely?
        for i in range(len(c)):
            # eslint-disable-next-line no-param-reassign
            # d[i] = d[i] or []#this might not work well
            for j in range(0, i):  # (let j = 0; j <= i; j++) {
                # console.log(c[i], c[j], distance(c[i], c[j]))
                new_distance = (
                    float("inf") if (i == j) else distance(c[i], c[j])
                )
                # eslint-disable-next-line no-param-reassign
                d[i][j] = new_distance
                # eslint-disable-next-line no-param-reassign
                d[j][i] = new_distance

        # the while condition could die???
        match = closet_match(d, min_distance)
        while match is not None:
            c[match["i"]] = merge(c[match["i"]], c[match["j"]])
            # remove the jth cluster
            del c[match["j"]]
            # remove the jth column
            for i in range(len(d)):
                del d[i][match["j"]]
            # remove the jth row
            del d[match["j"]]

            # recompute the distance matrix
            # for (let i = 0; i < d.length; i++) {
            for i in range(len(d)):
                new_distance = (
                    float("inf")
                    if i == match["i"]
                    else distance(c[match["i"]], c[i])
                )
                # eslint-disable-next-line no-param-reassign
                d[match["i"]][i] = new_distance
                # eslint-disable-next-line no-param-reassign
                d[i][match["i"]] = new_distance

            # compute the next match
            match = closet_match(d, min_distance)

        return c

    # make work with a proper object...
    def cluster(self, distance_func=distance):
        self.hierachical_cluster(
            distance_func,
            merge,
            closet_match,
            self.c,
            self.d,
            self.options["min_distance"],
        )
        return self.c
