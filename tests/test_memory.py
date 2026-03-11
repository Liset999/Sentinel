from collector.memory import parse_meminfo, get_memory_usage_percent


def test_parse_meminfo_basic():
    lines = [
        "MemTotal:       1000 kB\n",
        "MemFree:         200 kB\n",
        "MemAvailable:    400 kB\n",
    ]

    data = parse_meminfo(lines)

    assert data["MemTotal"] == 1000
    assert data["MemFree"] == 200
    assert data["MemAvailable"] == 400


def test_get_memory_usage_percent_from_fake_file(tmp_path):
    fake = tmp_path / "meminfo"
    fake.write_text(
        "MemTotal:       1000 kB\n"
        "MemFree:         200 kB\n"
        "MemAvailable:    400 kB\n",
        encoding="utf-8",
    )

    usage = get_memory_usage_percent(str(fake))

    assert usage == 60.0
