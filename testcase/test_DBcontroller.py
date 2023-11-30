import unittest
from unittest.mock import MagicMock, patch
from operations.controller.DBcontroller import Database  # 替换为实际的模块名

class TestDatabase(unittest.TestCase):

    @patch('operations.controller.DBcontroller.pymysql')
    def setUp(self, mock_pymysql):
        self.mock_conn = mock_pymysql.connect.return_value
        self.mock_cursor = self.mock_conn.cursor.return_value
        self.db = Database()

    def test_create_table(self):
        self.db.create_table('test_table', 'id INT')
        self.mock_cursor.execute.assert_called_with('CREATE TABLE test_table (id INT)')
        self.mock_conn.commit.assert_called_once()

    def test_insert(self):
        self.db.insert('test_table', ('value1', 'value2'))
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()

    def test_update(self):
        self.db.update('test_table', 'column1', 'value1', 'condition1')
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()

    def test_delete(self):
        self.db.delete('test_table', 'condition1')
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()

    def test_select(self):
        self.mock_cursor.fetchall.return_value = [('row1', 'row2')]
        self.mock_cursor.description = [('column1',), ('column2',)]
        df = self.db.select('test_table')
        self.mock_cursor.execute.assert_called_once()
        self.assertEqual(df.shape[0], 1)  # 验证返回的 DataFrame 行数

    def test_close(self):
        self.db.close()
        self.mock_cursor.close.assert_called_once()
        self.mock_conn.close.assert_called_once()

    def tearDown(self):
        self.db.close()

if __name__ == '__main__':
    unittest.main()

