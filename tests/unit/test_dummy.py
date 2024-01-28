"""Test dummy."""

from drivel_backend.dummy import add_one


def test_add_one() -> None:
    assert add_one(1) == 2
    assert add_one(2) == 3
    assert add_one(3) == 4
