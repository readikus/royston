# Royston

An open source, real time trend detection framework written in Python. This project uses machine learning to detect trends in text over time.

Trends are identified by detecting phrases that start occurring much more frequently than those that don't typically occur. Various natural language processing and data science techniques are used to ensure similar words are modelled together (i.e. "cycle", "cycling" and "cyclist" all reduce down to a common word form, such as "cycle").

Documents can be grouped by a subject, so it is possible to detect "localised" trends. Similar phrases tend to relate to a particular trend, so hierachical clustering is used to make sure documents related to the same trend are grouped, rather than creating two "trends" about the same thing. For example, "doping scandal" and "Tour de France" are likely to be about the same thing...allegedly.

Based on [`ramekin`](https://github.com/readikus/ramekin), but going to take it further to do real time detection and maintaining models rather than creating them each time.

## Installation and basic usage

We are going to create a royston to contain a set of news articles, and then find the trends.

First we will install the package via `pip` by typing the following into the command line:

```
pip3 install royston
```
Also install a couple of extra dependancies we will need for the example:

```
pip3 install datetime pytz
```

The following script creates some simple documents and adds them to a `royston` (also shipped in the `examples` directory):

```
from royston.royston import Royston
from datetime import datetime as dt
import pytz

roy = Royston()

# ingest a few documents
roy.ingest({ 'id': '123', 'body': 'Random text string', 'date': dt.now(pytz.UTC) })
roy.ingest({ 'id': '456', 'body': 'Antoher random string', 'date': dt.now(pytz.UTC) })

# find the trends - with this example, it won't find anything, as it's only got two stories!
trends = roy.trending()
print(trends)
```

## Configuration Options

### Constructor:

This package is heavily configurable to allow us to tune how we look for emerging trends. The default options have been set for the most common use case that looks at new trends that have emerged over the last 24 hours.

Currently, the main way of tuning these parameters is controlled by passing the Royston constructor an `options` dict with the following attributes:

| Attribute      | Type   | Default | Description                      |
|----------------|--------|---------|----------------------------------|
| `min_trend_freq` | `int` | 4 | A threshold for the minimum number of times a phrase has to occur in a single day before it can even be considered a trend for a given subject. |
| `history_days` | `int` | 90 | The context of the number of days to consider for the history. This means we look at how often a phrase has occured over this period, and get an idea of typical use. |
| `trend_days` | `int` | 1 | The period of time in which we want to look for trends. With the default of 1, we are looking at documents from the last day to see if new trends have emerged during that time compared with the typical use period defined by `history_days` |
| `max_n` | `int` | 6 | The maximum size of the n-gram window (i.e. the window size of each phrase) |
| `keep_stops` | `Boolean` | `False` | Keep stop words, based on the `nltk` stopword list |
| `history_frequency_tolerance` | `float` | 1.6 | Factor the history count by this amount to handle words that just didn't get mentioned in the history period. This usefulness of this is in review, and it is likely to be removed in future (or at least set to 1 by default). |
| `trends_top_n` | `int` | 8 | The maximum number of trends to return |

Disclaimer: the following options are currently supported but expected to change significantly in future releases:

| Attribute       | Type       | Default | Description                      |
|-----------------|------------|---------|----------------------------------|
| `start`         | `datetime` | now - trend_days | The start of the "trend" period (i.e. a day ago) |
| `end`           | `datetime` | now              | The end of the "trend" period  | 
| `history_start` | `datetime` | `start`          | Start of the trend period (i.e. `history_days` before `end`) |
| `history_end`   | `datetime` | `end`            | Start of the trend period (i.e. `history_days` before `end`) |

Currently they are calculate in the constructor only, which is stupid, as we want this to run in realtime and adapt each time the `trend` method is called.

## Running tests

```
poetry run test
```

Run coverage reports:

```
poetry run coverage
```

## Distribute

This now uses poetry for package management, which can be done with the following command:

```poetry build && poetry publish``

## Contribute?

This is still in the early stages of being ported over from JavaScript, and any help would be appreciated. The issues contain a lot of features that are needed. Please get in touch via [LinkedIn](https://www.linkedin.com/in/ianreadnorwich/) and I can talk you thought anything.

Main concerns are:

* 100% test coverage.
* Retain the document format
