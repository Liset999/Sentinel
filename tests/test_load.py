import unittest
import os
from collector.load import parse_loadavg  # 根据你实际的包结构导入


class TestCollector(unittest.TestCase):
    def test_loadavg_happy_path(self):
        # 1. 准备假文件
        test_file = "dummy_load.txt"
        with open(test_file, "w") as f:
            f.write("0.50 0.60 0.70 1/100 12345")

        # 2. 调用你的函数（传入假文件路径）
        result = parse_loadavg(test_file)

        # 3. 断言验证
        self.assertEqual(result['load1'], 0.50)

        # 4. 清理现场
        os.remove(test_file)


if __name__ == '__main__':
    unittest.main()
