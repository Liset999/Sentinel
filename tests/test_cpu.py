from collector.cpu import parse_cpu_times


def test_parse_cpu_times_basic():
    sample = "cpu  100 20 30 400 5 6 7 8 0 0\n"
    data = parse_cpu_times(sample)

    assert data["user"] == 100
    assert data["nice"] == 20
    assert data["system"] == 30
    assert data["idle"] == 400
    assert data["iowait"] == 5
    assert data["irq"] == 6
    assert data["softirq"] == 7
    assert data["steal"] == 8

def test_parse_cpu_times_invalid():
    bad = "intr 1 2 3\n"

    try:
        parse_cpu_times(bad)
        assert False
    except Exception:
        assert True
