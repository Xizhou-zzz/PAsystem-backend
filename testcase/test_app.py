import unittest
from app import app
from unittest.mock import patch
import json

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        # 创建一个测试客户端
        app.testing = True
        self.client = app.test_client()

    @patch('operations.functions.check')
    def test_login(self, mock_check):
        # 模拟 'check' 函数的行为
        mock_check.return_value = (1, 'admin')

        # 发送模拟的 POST 请求到 '/api/login'
        response = self.client.post('/api/login', json={
            'username': 'test_user',
            'password': 'test_password'
        })

        # 检查响应数据
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'status': 'ok', 'access': 'admin'})

    # 添加更多测试用例...
    @patch('operations.functions.create_peer_table')
    def test_create_peer_evaluations_success(self, mock_create_peer_table):
        # 模拟 'create_peer_table' 函数的行为，假设成功创建了互评表
        mock_create_peer_table.return_value = 'peer_table_name'

        # 发送模拟的 POST 请求到 '/api/peer-evaluations'
        response = self.client.post('/api/peer-evaluations', json={
            'usernames': ['student1', 'student2'],
            'homework': {'name': 'test_homework', 'date': '2021_11_23'}
        })

        # 检查响应数据
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'status': 'success', 'message': 'Peer evaluations created successfully.'})

    @patch('operations.functions.create_peer_table')
    def test_create_peer_evaluations_failure(self, mock_create_peer_table):
        # 模拟 'create_peer_table' 函数的行为，假设创建互评表失败
        mock_create_peer_table.return_value = None

        # 发送模拟的 POST 请求到 '/api/peer-evaluations'
        response = self.client.post('/api/peer-evaluations', json={
            'usernames': ['student1', 'student2'],
            'homework': {'name': 'test_homework', 'date': '2021_11_23'}
        })

    @patch('operations.functions.get_evaluations')
    def test_get_peer_evaluations(self, mock_get_evaluations):
        # 模拟 'get_evaluations' 函数的行为
        mock_get_evaluations.return_value = ['evaluation1', 'evaluation2']

        # 设置模拟的 session
        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = 'test_user'

            # 发送模拟的 GET 请求到 '/api/peer-evaluations'
            response = self.client.get('/api/peer-evaluations')

        # 检查响应数据
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'evaluations': ['evaluation1', 'evaluation2']})

    @patch('operations.functions.get_data')
    def test_homework_datasource(self, mock_get_data):
        # 模拟 'get_data' 函数的行为
        mock_get_data.return_value = {'data': 'some_data'}

        # 发送模拟的 POST 请求到 '/Homework_platform/correction'
        response = self.client.post('/Homework_platform/correction', json={'key': 'value'})

        # 检查响应数据
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'data': 'some_data'})

    def tearDown(self):
        # 清理代码（如果有需要）
        pass

if __name__ == '__main__':
    unittest.main()

