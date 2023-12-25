import requests
from flask import Flask, request, jsonify, session, redirect

from flask_session import Session
from operations import functions

from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'sbyp'

# @app.before_request
# def process_request():
#     # 判断请求路径是否为 API 请求
#     if not request.path.startswith('/api'):
#         # 将非 API 请求转发到另一个端口
#         return redirect('http://localhost:8000' + request.path, code=307)



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
        session['username'] = username
        res = jsonify({'status': 'ok', 'access': access, 'cookie': username})
        return res
    elif valid == 0:
        return jsonify({'status': 'error', 'message': 'User does not exist.'})
    elif valid == -1:
        return jsonify({'status': 'error', 'message': 'Password is error.'})


# 此函数用来创建一个作业的"互评关系"表，由老师执行“开启互评”触发
@app.route('/api/peer-evaluations', methods=['POST'])
def create_peer_evaluations():
    data = request.get_json()
    usernames = data['usernames']  # 获取前端传输的学生用户名列表
    homework = data['homework']  # 获取前端传输的该作业信息
    # 调用创建互评关系表的函数
    table_name = functions.create_peer_table(usernames, homework)  # 返回还不完善

    if table_name:
        return jsonify({'status': 'success', 'message': 'Peer evaluations created successfully.'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to create peer evaluations.'})


# 此函数用来获取到登录用户的"互评关系"表，由学生执行“查看我需要的互评”触发
@app.route('/api/peer-evaluations', methods=['GET'])
def get_peer_evaluations():
    username = session['username']  # 从 Session 中获取用户名

    # 根据用户名在互评记录表中查找相关记录
    evaluations = functions.get_evaluations(username)

    # 返回查询结果
    return jsonify({'evaluations': evaluations})


@app.route('/Homework_platform/correction', methods=['POST'])
def homework_datasource():
    print("数据请求")
    # 从前端获取请求体中的数据
    body = request.json
    # 根据需要从数据库或其他数据源获取数据
    datasource = functions.get_data()
    return jsonify(datasource)


################
# 分割线  admin #
################
@app.route('/teaching_manage/course_manage/get', methods=['GET'])
def course_get_data():
    username = request.cookies.get('username')
    session_info = session.get(username)  # 从前端中获取当前登录用户的用户名
    print(f'homework_platform-get: sesion_info: {session_info}')
    course_data = functions.get_course_data()
    return jsonify(course_data)


@app.route('/teaching_manage/course_manage/insert', methods=['POST'])
def course_insert():
    data = request.json
    status = functions.course_ins(data)
    if status:
        return jsonify({'status': 'success', 'message': '1 row insert successfully.'})
    else:
        return jsonify({'status': 'failure', 'message': 'insert failed.'})


@app.route('/teaching_manage/course_manage/delete', methods=['POST'])
def course_delete():
    data = request.json
    course_id_to_delete = data['course_id']
    status = functions.course_del(course_id_to_delete)
    if status:
        return jsonify({'status': 'success', 'message': '1 row deleted successfully.'})
    else:
        return jsonify({'status': 'failure', 'message': 'delete failed.'})


##################
# 分割线  teacher #
##################
@app.route('/homework_platform/homework_manage/get', methods=['GET'])
def homework_get_data():
    username = request.cookies.get('username')
    session_info = session.get(username)  # 从前端中获取当前登录用户的用户名
    print(f'homework_platform-get: sesion_info: {session_info}')
    homework_data = functions.get_homework_data('teacher1')
    return jsonify(homework_data)

@app.route('/homework_platform/homework_manage/create', methods=['POST'])
def create_homework():
    teacher_name = session.get('username')  # 从前端中获取当前登录用户的用户名
    print(f"{teacher_name} -- request to create homework")
    homework_data = request.json  # 从请求的 JSON 数据中获取作业信息
    status = functions.insert_homework(homework_data, teacher_name)
    if status:
        return jsonify({'status': 'success', 'message': '作业已创建'})
    else:
        return jsonify({'status': 'failure', 'message': 'create failed.'})


@app.route('/Course_platform_t/Student_grade/delete', methods=['DELETE'])
def grade_delete():
    return True


@app.route('/Homework_platform/homework_manage/add', methods=['POST'])
def add_homework():
    data = request.json
    status = functions.add_homework(data)
    if status:
        return jsonify({'status': 'success', 'message': 'Homework added successfully.'})
    else:
        return jsonify({'status': 'failure', 'message': 'adding homework failed.'})


@app.route('/Homework_platform/homework_manage/data_analysis', methods=['GET'])
def data_analysis():
    data = functions.get_data()
    report = functions.generate_report(data)
    return jsonify({'status': 'success', 'report': report})


##################
# 分割线  student #
##################
@app.route('/Homework_platform/homework_submission/submit', methods=['POST'])
def submit_homework():
    data = request.json
    status = functions.submit_homework(data)
    if status:
        return jsonify({'status': 'success', 'message': 'Homework submitted successfully.'})
    else:
        return jsonify({'status': 'failure', 'message': 'submitting homework failed.'})


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'

    # 需要设置 SESSION_COOKIE_HTTPONLY 为 False
    app.config['SESSION_COOKIE_HTTPONLY'] = False

    Session(app)
    app.run()
