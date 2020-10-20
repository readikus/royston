# royston

An open source, real time trend detection framework written in Python. This project uses machine learning to detect trends in text over time.

Trends are identified by detecting phrases that start occurring much more frequently than those that don't typically occur. Various natural language processing and data science techniques are used to ensure similar words are modelled together (i.e. "cycle", "cycling" and "cyclist" all reduce down to a common word form, such as "cycle").

Documents can be grouped by a subject, so it is possible to detect "localised" trends. Similar phrases tend to relate to a particular trend, so hierachical clustering is used to make sure documents related to the same trend are grouped, rather than creating two "trends" about the same thing. For example, "doping scandal" and "Tour de France" are likely to be about the same thing...allegedly.

Based on [`ramekin`](https://github.com/readikus/ramekin), but going to take it further to do real time detection and maintaining models rather than creating them each time.

## Running tests

```
coverage run -m unittest royston.tests.royston_test -v
coverage report -m  royston/royston.py
```

## Contribute?

This is still in the early stages of being ported over from JavaScript, and any help would be appreciated. The issues contain a lot of features that are needed. Please get in touch via [LinkedIn](https://www.linkedin.com/in/ianreadnorwich/) and I can talk you thought anything.
