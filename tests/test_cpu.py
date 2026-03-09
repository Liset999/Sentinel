from collector.cpu import parse_cpu_times, calculate_cpu_usage


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
    except ValueError:
        assert True


def test_calculate_cpu_usage_basic():
    prev = {
        "user": 100,
        "nice": 0,
        "system": 100,
        "idle": 700,
        "iowait": 50,
        "irq": 10,
        "softirq": 20,
        "steal": 0,
    }

    curr = {
        "user": 150,
        "nice": 0,
        "system": 150,
        "idle": 800,
        "iowait": 50,
        "irq": 10,
        "softirq": 40,
        "steal": 0,
    }

    usage = calculate_cpu_usage(prev, curr)

    assert round(usage, 2) == 54.55
