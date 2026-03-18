from exporter.app import get_tcp_metric_value, build_metrics_snapshot


def test_get_tcp_metric_value_returns_existing_value():
    stats = {
        "TIME_WAIT": 12,
        "ESTABLISHED": 5,
    }

    result = get_tcp_metric_value(stats, "TIME_WAIT")

    assert result == 12


def test_get_tcp_metric_value_returns_zero_for_missing_key():
    stats = {
        "TIME_WAIT": 12,
    }

    result = get_tcp_metric_value(stats, "CLOSE_WAIT")

    assert result == 0


def test_build_metrics_snapshot_contains_expected_keys():
    snapshot = build_metrics_snapshot()

    expected_keys = {
        "cpu_usage_ratio",
        "mem_available_kb",
        "mem_total_kb",
        "load1",
        "tcp_time_wait_count",
        "tcp_close_wait_count",
        "tcp_established_count",
        "zombie_process_count",
    }

    assert set(snapshot.keys()) == expected_keys


def test_build_metrics_snapshot_initial_values_are_none():
    snapshot = build_metrics_snapshot()

    assert snapshot["cpu_usage_ratio"] is None
    assert snapshot["mem_available_kb"] is None
    assert snapshot["mem_total_kb"] is None
    assert snapshot["load1"] is None
    assert snapshot["tcp_time_wait_count"] is None
    assert snapshot["tcp_close_wait_count"] is None
    assert snapshot["tcp_established_count"] is None
    assert snapshot["zombie_process_count"] is None

from exporter import app


def test_update_metrics_sets_expected_values(monkeypatch):
    app._prev_cpu_times = [100, 0, 100, 100]

    monkeypatch.setattr(app, "read_proc_stat", lambda: "fake /proc/stat text")
    monkeypatch.setattr(app, "parse_cpu_times", lambda text: [200, 0, 100, 200])
    monkeypatch.setattr(app, "get_cpu_usage_ratio", lambda prev, curr: 0.5)

    monkeypatch.setattr(app, "get_memory_info", lambda: {
        "MemAvailable": 12345,
        "MemTotal": 67890,
    })

    monkeypatch.setattr(app, "get_load_average", lambda: {
        "load1": 1.25,
    })

    monkeypatch.setattr(app, "get_tcp_stats", lambda: {
        "TIME_WAIT": 7,
        "CLOSE_WAIT": 3,
        "ESTABLISHED": 11,
    })

    monkeypatch.setattr(app, "count_zombie_processes", lambda: 2)

    before_errors = app.exporter_update_errors._value.get()

    app.update_metrics()

    after_errors = app.exporter_update_errors._value.get()

    assert app.cpu_usage._value.get() == 0.5
    assert app.mem_available._value.get() == 12345
    assert app.mem_total._value.get() == 67890
    assert app.load1._value.get() == 1.25
    assert app.tcp_time_wait._value.get() == 7
    assert app.tcp_close_wait._value.get() == 3
    assert app.tcp_established._value.get() == 11
    assert app.zombie_count._value.get() == 2
    assert after_errors == before_errors

def test_update_metrics_increments_error_counter_on_memory_failure(monkeypatch):
    app._prev_cpu_times = [100, 0, 100, 100]

    monkeypatch.setattr(app, "read_proc_stat", lambda: "fake /proc/stat text")
    monkeypatch.setattr(app, "parse_cpu_times", lambda text: [200, 0, 100, 200])
    monkeypatch.setattr(app, "get_cpu_usage_ratio", lambda prev, curr: 0.5)

    def fake_memory_failure():
        raise RuntimeError("memory collector failed")

    monkeypatch.setattr(app, "get_memory_info", fake_memory_failure)
    monkeypatch.setattr(app, "get_load_average", lambda: {"load1": 1.0})
    monkeypatch.setattr(app, "get_tcp_stats", lambda: {
        "TIME_WAIT": 1,
        "CLOSE_WAIT": 2,
        "ESTABLISHED": 3,
    })
    monkeypatch.setattr(app, "count_zombie_processes", lambda: 0)

    before_errors = app.exporter_update_errors._value.get()

    app.update_metrics()

    after_errors = app.exporter_update_errors._value.get()

    assert after_errors == before_errors + 1
    assert app.cpu_usage._value.get() == 0.5
    assert app.load1._value.get() == 1.0
    assert app.tcp_time_wait._value.get() == 1
    assert app.tcp_close_wait._value.get() == 2
    assert app.tcp_established._value.get() == 3
    assert app.zombie_count._value.get() == 0
