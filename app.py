from flask import Flask, request, jsonify, session
from operations import functions
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'penggeniubi'


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
        # 保存用户名到 Session
        session['username'] = username
        return jsonify({'status': 'ok', 'access': access})
    elif valid == 0:
        return jsonify({'status': 'error', 'message': 'User does not exist.'})


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
    username = session.get('username')  # 从 Session 中获取用户名

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
        return jsonify({'status': 'failure', 'message': 'insert failed.'})


##################
# 分割线  teacher #
##################
@app.route('/Course_platform_t/Student_grade/delete', methods=['DELETE'])
def grade_delete():
    return True


##################
# 分割线  student #
##################

if __name__ == '__main__':
    app.run()
