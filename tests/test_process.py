import unittest
import os
import shutil

# 假设你的主代码文件叫 process.py
from collector.process import parse_proc, list_proc


class TestProcessCollector(unittest.TestCase):
    def setUp(self):
        # 1. 制造一个假的 proc 目录
        self.fake_proc = "./dummy_proc"
        os.makedirs(self.fake_proc, exist_ok=True)

        # 2. 制造一个假的进程目录 (PID为1234)
        pid_dir = os.path.join(self.fake_proc, "1234")
        os.makedirs(pid_dir, exist_ok=True)

        # 3. 往里面写一个假的 stat 文件，状态故意设为 Z (Zombie)
        # 注意：这里我们故意在括号里加了空格，用来测试你的 rfind(')') 是否生效
        stat_file = os.path.join(pid_dir, "stat")
        with open(stat_file, "w") as f:
            f.write("1234 (fake zombie) Z 1 1234 1234 0 -1 4194560 ...")

        # [你需要补充] 4. 再制造一个伪造的目录，比如 PID为 5678，状态设为 R (Running)
        pid_dir_2 = os.path.join(self.fake_proc, "5678")
        os.makedirs(pid_dir_2, exist_ok=True)

        stat_file_2 = os.path.join(pid_dir_2, "stat")
        with open(stat_file_2, "w") as f:
            # 这里状态改成 R，进程名也可以随便写
            f.write("5678 (my running process) R 1 5678 5678 0 -1 4194560 ...")

    def test_parse_proc(self):
        # 1. 调用我们的函数，传入假目录 self.fake_proc
        result = parse_proc(self.fake_proc)

        # 2. 断言：检查结果对不对
        self.assertEqual(result['Zombie'], 1)  # 我们造了 1 个僵尸进程
        self.assertEqual(result['Running'], 1)  # 我们造了 1 个运行进程

    def tearDown(self):
        # 5. 打扫战场：连同目录和里面的文件全部删除
        if os.path.exists(self.fake_proc):
            shutil.rmtree(self.fake_proc)


if __name__ == '__main__':
    unittest.main()
