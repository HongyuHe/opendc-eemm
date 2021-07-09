import pytest

@pytest.mark.parametrize('value, expected', [('hi', 'hi')])
def test_hello(value, expected):
    assert value == expected