def assert_headers_equal(headers1, headers2):
    assert len(headers1) == len(headers2)

    # normalize headers
    headers1 = _normalize_headers(headers1)
    headers2 = _normalize_headers(headers2)

    for key, value in headers1.items():
        assert key in headers2
        if key in ["date", "cf-ray"]:
            continue
        assert value == headers2[key], (
            f"Header {key} is not equal. {value} != {headers2[key]}"
        )


def _normalize_headers(headers):
    return {key.lower(): value for key, value in headers.items()}
