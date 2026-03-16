import pytest

from collector.process import parse_process_stat,count_zombie_processes


def test_parse_process_stat_sleeping():
    sample = "1 (systemd) S 0 1 1 0 -1 4194560"
    assert parse_process_stat(sample) == "S"


def test_parse_process_stat_zombie():
    sample = "999 (zombie_maker) Z 1 1 1 0 -1 4194560"
    assert parse_process_stat(sample) == "Z"


def test_parse_process_stat_empty():
    with pytest.raises(ValueError):
        parse_process_stat("")

def test_count_zombie_processes(tmp_path):
    proc_root = tmp_path

    pid1 = proc_root / "123"
    pid1.mkdir()
    (pid1 / "stat").write_text("123 (worker) S 1 2 3 4 5\n", encoding="utf-8")

    pid2 = proc_root / "456"
    pid2.mkdir()
    (pid2 / "stat").write_text("456 (zombie_maker) Z 1 2 3 4 5\n", encoding="utf-8")

    (proc_root / "net").mkdir()

    assert count_zombie_processes(str(proc_root)) == 1

def test_count_zombie_processes_skips_missing_stat(tmp_path):
    proc_root = tmp_path

    pid1 = proc_root / "123"
    pid1.mkdir()
    (pid1 / "stat").write_text("123 (zombie_maker) Z 1 2 3 4 5\n", encoding="utf-8")

    pid2 = proc_root / "456"
    pid2.mkdir()

    assert count_zombie_processes(str(proc_root)) == 1

def test_count_zombie_processes_skips_invalid_stat(tmp_path):
    proc_root = tmp_path

    pid1 = proc_root / "123"
    pid1.mkdir()
    (pid1 / "stat").write_text("123 (zombie_maker) Z 1 2 3 4 5\n", encoding="utf-8")

    pid2 = proc_root / "456"
    pid2.mkdir()
    (pid2 / "stat").write_text("bad stat content\n", encoding="utf-8")

    assert count_zombie_processes(str(proc_root)) == 1
