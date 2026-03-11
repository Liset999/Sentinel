from collector.load import parse_loadavg


def test_parse_loadavg_basic():
    text = "0.00 0.01 0.05 1/123 4567"
    data = parse_loadavg(text)

    assert data["load1"] == 0.00
    assert data["load5"] == 0.01
    assert data["load15"] == 0.05


def test_parse_loadavg_invalid():
    bad = "0.00 0.01"

    try:
        parse_loadavg(bad)
        assert False
    except ValueError:
        assert True
