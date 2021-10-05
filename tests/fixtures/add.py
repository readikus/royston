import pytest


@pytest.fixture
def add(x, y):
    x + y
