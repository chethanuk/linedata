from line_level_data_collection.handlers.verification import base_64_encode_json, base_64_decode_json


def test_encode_decode():
    test_content = {"foo": "bar"}
    result = base_64_encode_json(test_content)
    assert isinstance(result, str)
    assert base_64_decode_json(result) == test_content
