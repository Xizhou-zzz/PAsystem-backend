from flask import Flask, request, jsonify
from operations import functions
app = Flask(__name__)


# 登录相关方法
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    print(f"用户 {username} 请求登录")

    # 在这里实现根据用户名查询密码的逻辑
    valid, access = functions.check(username, password)

    # 1:许可，0:不存在，-1:密码错误
    if valid == 1:
        return jsonify({'status': 'ok', 'access': access})
    elif valid == 0:
        return jsonify({'status': 'error', 'message': 'User does not exist.'})


@app.route('/Homework_platform/correction', methods=['POST'])
def homework_datasource():
    print("数据请求")
    # 从前端获取请求体中的数据
    body = request.json
    # 根据需要从数据库或其他数据源获取数据
    datasource = functions.get_data()
    return jsonify(datasource)






if __name__ == '__main__':
    app.run()
