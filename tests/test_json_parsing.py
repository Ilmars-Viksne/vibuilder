import pytest
from agent.parsing import extract_json_object, extract_json_array

def test_extract_json_object():
    assert extract_json_object('{"a": 1}') == {"a": 1}
    assert extract_json_object('Some prose before {"a": 1} and after') == {"a": 1}
    assert extract_json_object('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json_object('```\n{"a": 1}\n```') == {"a": 1}

def test_extract_json_array():
    assert extract_json_array('[1, 2, 3]') == [1, 2, 3]
    assert extract_json_array('Here is a list: [1, 2, 3] enjoy') == [1, 2, 3]
    assert extract_json_array('```json\n["a", "b"]\n```') == ["a", "b"]
