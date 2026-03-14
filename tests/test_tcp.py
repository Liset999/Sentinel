from collector.tcp import parse_tcp_table


def test_parse_tcp_table_basic():
    sample = """  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
   0: 0100007F:1770 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 12345 1 0000000000000000 100 0 0 10 0
   1: 0100007F:0016 0100007F:A3F2 01 00000000:00000000 00:00000000 00000000  1000        0 12346 1 0000000000000000 20 4 30 10 -1
   2: 0100007F:0017 0100007F:A3F3 06 00000000:00000000 00:00000000 00000000  1000        0 12347 1 0000000000000000 20 4 30 10 -1
   3: 0100007F:0018 0100007F:A3F4 08 00000000:00000000 00:00000000 00000000  1000        0 12348 1 0000000000000000 20 4 30 10 -1
"""
    stats = parse_tcp_table(sample)

    assert stats["LISTEN"] == 1
    assert stats["ESTABLISHED"] == 1
    assert stats["TIME_WAIT"] == 1
    assert stats["CLOSE_WAIT"] == 1


def test_parse_tcp_table_unknown_state():
    sample = """  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
   0: 0100007F:1770 00000000:0000 FF 00000000:00000000 00:00000000 00000000  1000        0 12345 1 0000000000000000 100 0 0 10 0
"""
    stats = parse_tcp_table(sample)

    assert stats["UNKNOWN_FF"] == 1


def test_parse_tcp_table_empty():
    assert parse_tcp_table("") == {}
