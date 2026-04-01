import unittest
import os
from collector.tcp import parse_tcp


class TestTCPCollector(unittest.TestCase):
    def setUp(self):
        # 1. 准备打扫战场的临时文件名
        self.test_file = "dummy_tcp.txt"

        # 2. 伪造一份极简的 /proc/net/tcp 内容
        # 注意：你需要保证第 34-35 个字符刚好是你想要的状态码（比如 01 和 0A）
        fake_data = """  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode                                                     
   0: 00000000:0016 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 12345 1 0000000000000000 100 0 0 10 0                     
   1: 0100007F:0016 0100007F:ABCD 01 00000000:00000000 00:00000000 00000000     0        0 12346 1 0000000000000000 100 0 0 10 0
"""
        # 把 fake_data 写进 self.test_file 里
        with open(self.test_file, "w") as f:
            f.write(fake_data)

    def test_parse_tcp(self):
        # 3. 把假文件路径传给你的函数
        metrics = parse_tcp(file_path=self.test_file)

        # 4. 断言！用上帝视角检查数据对不对
        # 假数据里有一个 0A (LISTEN) 和一个 01 (ESTABLISHED)
        self.assertEqual(metrics["LISTEN"], 1)
        self.assertEqual(metrics["ESTABLISHED"], 1)
        self.assertEqual(metrics["TIME_WAIT"], 0)  # 没出现的应该是 0

    def tearDown(self):
        os.remove(self.test_file)
        pass


if __name__ == '__main__':
    unittest.main()
