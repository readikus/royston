# content of conftest.py
import pytest
from datetime import datetime as dt
import json
import os
import pytz
from dateutil.relativedelta import relativedelta as delta

# ensure a consistent relative timestamp
now = dt.now(pytz.UTC)
recent = now - delta(hours=1)

history_doc_1 = {
    "id": "7",
    "body": "Some random old string",
    "date": now - delta(months=1),
}
history_doc_2 = {
    "id": "8",
    "body": "Another really old random string",
    "date": now - delta(months=2),
}
subject_doc_1 = {
    "id": "1",
    "body": "Random text string",
    "date": recent,
    "subject": "wombles",
}
subject_doc_2 = {
    "id": "2",
    "body": "I tie laces with string",
    "date": recent,
    "subject": "wombles",
}
subject_doc_3 = {
    "id": "3",
    "body": "Can you string a sentence together",
    "date": recent,
    "subject": "wombles",
}
subject_doc_4 = {
    "id": "4",
    "body": "My fave theory is string theory",
    "date": recent,
    "subject": "wombles",
}
subject_doc_5 = {
    "id": "5",
    "body": "I live on a shoe string",
    "date": recent,
    "subject": "wombles",
}


@pytest.fixture
def input_value():
    input = 39
    return input


@pytest.fixture
def history_docs():
    return [history_doc_1, history_doc_2]


@pytest.fixture
def doc_1():
    return {
        "id": "123",
        "body": "Random text string",
        "date": recent,
    }


@pytest.fixture
def doc_2():
    return {
        "id": "456",
        "body": "Antoher random string",
        "date": recent,
    }


@pytest.fixture
def no_id_test_doc():
    return {"body": "Another random string", "date": recent}


@pytest.fixture
def no_date_test_doc():
    return {"id": "123", "body": "Another random string"}


@pytest.fixture
def used_phrases():
    return [
        ("antoher",),
        ("antoher", "random"),
        ("antoher", "random", "string"),
        ("random",),
        ("random", "string"),
        ("random", "text"),
        ("random", "text", "string"),
        ("string",),
        ("text",),
        ("text", "string"),
    ]


@pytest.fixture
def subject_docs():
    return [
        subject_doc_1,
        subject_doc_2,
        subject_doc_3,
        subject_doc_4,
        subject_doc_5,
    ]


@pytest.fixture
def data_small():

    with open(
        os.path.dirname(__file__) + "/test-articles-small.json", "r"
    ) as article_file:
        article_data = article_file.read()

    return json.loads(article_data)


@pytest.fixture
def snapshot_options():
    return {
        "start": dt(2019, 1, 20, 0, 0, 1, tzinfo=pytz.UTC),
        "end": dt(2019, 1, 21, 23, 59, 5, tzinfo=pytz.UTC),
    }


default_options = {
    "start": now - delta(days=1),
    "end": now,
}

print("default_options", default_options)
default_history_options = {
    **default_options,
    "history_end": default_options["start"],
    "history_start": default_options["start"] - delta(days=30),
}


@pytest.fixture
def options():
    return {
        "start": now - delta(days=1),
        "end": now,
    }


@pytest.fixture
def all_options():
    return default_history_options


@pytest.fixture
def options_with_subject():
    return {**default_options, "subject": "wombles"}


@pytest.fixture
def past_history_options():
    return {
        "start": now - delta(years=2),
        "end": now - delta(years=1),
    }
