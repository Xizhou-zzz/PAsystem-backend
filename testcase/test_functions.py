import unittest
from unittest.mock import patch
import pandas as pd
from operations import functions

class TestFunctions(unittest.TestCase):

    @patch('operations.controller.DBcontroller.Database.select')
    def test_check_user_exists(self, mock_select):
        # 模拟数据库返回值，表示用户存在
        mock_select.return_value = pd.DataFrame({'password': ['test_password'], 'access': ['admin']})
        valid, access = functions.check('existing_user', 'test_password')
        self.assertEqual(valid, 1)
        self.assertEqual(access, 'admin')

    @patch('operations.controller.DBcontroller.Database.select')
    def test_check_user_not_exists(self, mock_select):
        # 模拟数据库返回空 DataFrame，表示用户不存在
        mock_select.return_value = pd.DataFrame()
        valid, access = functions.check('non_existing_user', 'test_password')
        self.assertEqual(valid, 0)
        self.assertIsNone(access)

    def test_get_evaluations(self):
        # 测试 get_evaluations 函数
        username = "test_user"
        result = functions.get_evaluations(username)
        self.assertEqual(result, username)

    def test_get_data(self):
        # 测试 get_data 函数
        data = functions.get_data()
        self.assertIsInstance(data, list)  # 验证返回类型为列表
        self.assertGreater(len(data), 0)  # 验证列表不为空

    @patch('operations.controller.DBcontroller.Database.create_table')
    @patch('operations.controller.DBcontroller.Database.insert')
    @patch('operations.controller.DBcontroller.Database.select')
    @patch('random.choice')
    def test_create_peer_table(self, mock_random_choice, mock_select, mock_insert, mock_create_table):
        mock_random_choice.side_effect = lambda x: x[0]  # 总是选择列表的第一个元素
        mock_select.return_value = pd.DataFrame()  # 模拟数据库 select 返回空 DataFrame

        usernames = ["student1", "student2", "student3"]
        homework = {"name": "test_homework", "date": "2021_11_23"}
        result = functions.create_peer_table(usernames, homework)

        # 验证是否调用了创建表和插入数据的方法
        mock_create_table.assert_called()
        mock_insert.assert_called()
        self.assertIsNone(result)  # 因为函数没有返回值，所以预期为 None

if __name__ == '__main__':
    unittest.main()
