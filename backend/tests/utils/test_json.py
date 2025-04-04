import json

import pytest

from utils.common.json import json_dumps, json_loads


def test_json_dumps_and_loads():
    test_data = {
        "string": "hello",
        "number": 42,
        "list": [1, 2, 3],
        "nested": {"key": "value"}
    }
    
    # Test dumps
    json_string = json_dumps(test_data)
    assert isinstance(json_string, str)
    
    # Test loads
    parsed_data = json_loads(json_string)
    assert parsed_data == test_data


def test_json_dumps_special_types():
    # Test with bytes
    assert json_dumps(b"hello") == '"hello"'
    
    # Test with None
    assert json_dumps(None) == 'null'


def test_json_loads_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        json_loads("invalid json") 