# content of conftest.py
import pytest
from datetime import datetime as dt
import json
import os
import pytz
from dateutil.relativedelta import relativedelta as delta

# ensure a consistent relative timestamp
now = dt.now(pytz.UTC)


@pytest.fixture
def input_value():
    input = 39
    return input


@pytest.fixture
def old_test_doc_1():
    return {
        "id": "123",
        "body": "Random text string",
        "date": dt(2000, 1, 20, 0, 0, 1, tzinfo=pytz.UTC),
    }


@pytest.fixture
def old_test_doc_2():
    return {
        "id": "456",
        "body": "Antoher random string",
        "date": dt(2000, 1, 12, 0, 0, 1, tzinfo=pytz.UTC),
    }


@pytest.fixture
def history_doc_1(scope="module"):
    return {
        "id": "7",
        "body": "Some random old string",
        "date": now - delta(months=1),
    }


@pytest.fixture
def history_doc_2(scope="module"):
    return {
        "id": "8",
        "body": "Another really old random string",
        "date": now - delta(months=2),
    }


@pytest.fixture
def test_doc():
    return {
        "id": "123",
        "body": "Random text string",
        "date": now,
    }


@pytest.fixture
def test_doc_2():
    return {
        "id": "456",
        "body": "Antoher random string",
        "date": now,
    }


@pytest.fixture
def no_id_test_doc():
    return {"body": "Another random string", "date": dt.now(pytz.UTC)}


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


subject_test_doc_1 = {
    "id": "1",
    "body": "Random text string",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}
subject_test_doc_2 = {
    "id": "2",
    "body": "I tie laces with string",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}
subject_test_doc_3 = {
    "id": "3",
    "body": "Can you string a sentence together",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}
subject_test_doc_4 = {
    "id": "4",
    "body": "My fave theory is string theory",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}
subject_test_doc_5 = {
    "id": "5",
    "body": "I live on a shoe string",
    "date": dt.now(pytz.UTC),
    "subject": "wombles",
}


@pytest.fixture
def subject_docs():
    return [
        subject_test_doc_1,
        subject_test_doc_2,
        subject_test_doc_3,
        subject_test_doc_4,
        subject_test_doc_5,
    ]


@pytest.fixture
def small_article_data():

    with open(
        os.path.dirname(__file__) + "/test-articles-small.json", "r"
    ) as article_file:
        article_data = article_file.read()

    return json.loads(article_data)


@pytest.fixture
def snapshot_test_time_options():
    return {
        "start": dt(2019, 1, 20, 0, 0, 1, tzinfo=pytz.UTC),
        "end": dt(2019, 1, 21, 23, 59, 5, tzinfo=pytz.UTC),
    }


default_options = {
    "start": now - delta(day=1),
    "end": dt.now(pytz.UTC),
}
default_history_options = {
    **default_options,
    "history_end": default_options["start"],
    "history_start": default_options["start"] - delta(days=30),
}


@pytest.fixture
def find_doc_options():
    return default_options


@pytest.fixture
def all_options():
    return default_history_options


@pytest.fixture
def find_doc_options_with_subject():
    return {**default_options, "subject": "wombles"}


@pytest.fixture
def find_doc_options_incomplete():
    return {
        "start": now - delta(months=1),
        "end": dt.now(),
    }


@pytest.fixture
def past_history_options():
    return {
        "start": now - delta(years=2),
        "end": now - delta(years=1),
    }
