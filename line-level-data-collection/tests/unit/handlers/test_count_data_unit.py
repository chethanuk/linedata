from line_level_data_collection.handlers.count_data import url_b64_encode_str, url_b64_decode_str


def test_encode_decode():
    test_content = '{}|;\''
    encoded = url_b64_encode_str(test_content)
    for char in test_content:
        assert char not in encoded
    decoded = url_b64_decode_str(encoded)
    assert decoded == test_content
