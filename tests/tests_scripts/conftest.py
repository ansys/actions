"""A module containing various reusable fixtures for the tests suite."""

import pytest


@pytest.fixture()
def cname():
    return "test.domain.com"
