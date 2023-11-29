import unittest
from unittest.mock import patch
from operations.functions import check  # 导入check函数
import pandas as pd

class TestCheckFunction(unittest.TestCase):

    @patch('operations.controller.DBcontroller.Database.select')
    def test_check_with_valid_credentials(self, mock_select):
        # 设置模拟对象的返回值
        mock_select.return_value = pd.DataFrame({
            'password': ['correct_password'],
            'access': ['admin']
        })

        # 调用测试函数
        result = check('valid_user', 'correct_password')

        # 断言
        self.assertEqual(result, (1, 'admin'))

    @patch('operations.controller.DBcontroller.Database.select')
    def test_check_with_invalid_credentials(self, mock_select):
        # 设置模拟对象返回空 DataFrame
        mock_select.return_value = pd.DataFrame()

        # 调用测试函数
        result = check('invalid_user', 'wrong_password')

        # 断言
        self.assertEqual(result, (0, None))

if __name__ == '__main__':
    unittest.main()
