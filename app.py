import requests
import random
import smtplib
from flask import Flask, request, jsonify, session, redirect
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
from email.header import Header
import os

from flask_session import Session
from operations import functions
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

code_cache = {}

# @app.before_request
# def process_request():
#     # 判断请求路径是否为 API 请求
#     if not request.path.startswith('/api'):
#         # 将非 API 请求转发到另一个端口
#         return redirect('http://localhost:8000' + request.path, code=307)

app.config['SECRET_KEY'] = 'sbyp'
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = '465'
app.config['MAIL_USERNAME'] = '1158398445@qq.com'
app.config['MAIL_PASSWORD'] = 'qezntdfxrygsfeec'
app.config['MAIL_USE_SSL'] = True

def send_email(email, code):
    sender = app.config['MAIL_USERNAME']
    receivers = [email]
    nickname = '汤臣一品业主委员会'
    nickname_encoded = Header(nickname, 'utf-8').encode()

    # 构建 From 字段
    from_email = app.config['MAIL_USERNAME']
    from_header = f'{nickname_encoded} <{from_email}>'  # From 字段形如： "昵称" <邮箱地址>

    # 构建邮件内容
    message = MIMEText('您的验证码为：' + code, 'plain', 'utf-8')
    message['From'] = Header(from_header)
    message['To'] = Header(email, 'utf-8')
    message['Subject'] = Header('邮箱验证码', 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        smtpObj.login(sender, app.config['MAIL_PASSWORD'])
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("ok")
        return True
    except Exception as e:
        print("邮件发送失败:", str(e))
    return False

@app.route('/sendcode', methods=['POST'])
def send_code():
    data = request.json
    email = data['email']
    # check if email exists in the database
    conn = mysql.connector.connect(host='localhost', user='root', password='20020830wyb2618', database='pa') # 修改为自己的数据库连接信息
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
    result = cursor.fetchall()
    if len(result) == 0:
        return jsonify({'message': '该邮箱未注册'}), 400
    # generate code and store it in the cache
    code = str(random.randint(100000, 999999))
    code_cache[email] = code  # 将验证码保存到全局变量中
    print(code)     # 我在这里输出一下正确的验证码，这样就不用进邮箱查看了，在后端命令行看看就行
    # store the code in redis or other caching service
    # send email
    if send_email(email, code):
        return jsonify({'message': '验证码已发送'}), 200
    else:
        return jsonify({'message': '验证码发送失败'}), 500

@app.route('/api/login_email', methods=['POST'])
def login_email():
    data = request.json
    email = data['email']
    code = data['code']
    # 修改为自己的数据库连接信息
    conn = mysql.connector.connect(host='localhost', user='root', password='20020830wyb2618', database='pa')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', (email,))      # check if email exists in the database
    result = cursor.fetchall()
    if len(result) == 0:
        return jsonify({'message': '该邮箱未注册'}), 400
    # check if the code is correct
    # get the code from redis or other caching service
    correct_code = code_cache.get(email)
    if correct_code is None:
        return jsonify({'message': '验证码过期或不存在'}), 400
    if code != correct_code:
        return jsonify({'message': '验证码错误'}), 400
    # login success
    return jsonify({'message': '登录成功', 'user': {'id': result[0][0], 'username': result[0][1], 'access': result[0][3]}}), 200


@app.route('/api/upload', methods=['POST'])
def upload_file():
    # upload_folder = 'uploads'
    # if not os.path.exists(upload_folder):
    #     os.makedirs(upload_folder)
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('C:\\Users\\jiexinXe\\Desktop\\Codefield\\Github\\PAsystem-backend\\uploads', filename))
        return 'File uploaded successfully'

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


@app.route('/api/courses', methods=['GET'])
def get_courses():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Ys012567',
        database='pa'
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM course')
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(courses)


@app.route('/api/user/<user_name>', methods=['GET'])
def get_user(user_name):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT username, id, access, email, address FROM users WHERE username = %s", (user_name,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/update', methods=['POST'])
def update_user():
    data = request.json
    user_id = data.get("id")  # 确保这与前端发送的数据匹配
    username = data.get("username")
    access = data.get("access")
    email = data.get("email")
    address = data.get("address")
    # 如果还有其他字段，继续添加

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
        )
        cursor = connection.cursor()
        cursor.execute(
            'UPDATE users SET username = %s, access = %s, email = %s, address = %s WHERE id = %s',
            (username, access, email, address, user_id)
        )
        connection.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify({"success": True})


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

@app.route('/api/people', methods=['GET'])
def get_people():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
        )
        cursor = connection.cursor(dictionary=True)

        # 获取学生数据
        cursor.execute("SELECT * FROM users WHERE access = 'student'")
        students = cursor.fetchall()

        # 获取教师数据
        cursor.execute("SELECT * FROM users WHERE access = 'teacher'")
        teachers = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"students": students, "teachers": teachers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取用户列表
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users')  # 确保表名和字段与数据库匹配
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 更新用户权限
@app.route('/api/users/<user_id>/access', methods=['POST'])
def update_access(user_id):
    new_access = request.json.get('access')
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
        )
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET access = %s WHERE id = %s", (new_access, user_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        print("An error occurred: {}".format(e))
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify({"success": True})

##################
# 分割线  teacher #
##################
@app.route('/homework_platform/homework_manage/get/<user_name>', methods=['GET'])
def homework_get_data():
    username = user_name
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

@app.route('/teaching_manage/course_manage/get/<user_name>', methods=['GET'])
def course_get_tdata(user_name):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM course WHERE main_teacher = %s", (user_name,))
        course_data = cursor.fetchall()
        cursor.close()
        connection.close()
        if course_data:
            return jsonify(course_data)
        else:
            return jsonify({"error": "Course not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/homework_manage/teacher_get/<user_name>', methods=['GET'])
def get_homeworks(user_name):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM homework, users WHERE users.username = %s and users.id = homework.teacher_id", (user_name,))
        # 打印 SQL 查询语句

        homework_data = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(homework_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route('/Course_platform_s/Mycourse/get/<user_name>', methods=['GET'])
def course_get_sdata(user_name):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM course,studying WHERE studying.student_name = %s and studying.course_id = course.course_id", (user_name,))
        course_data = cursor.fetchall()
        cursor.close()
        connection.close()
        if course_data:
            return jsonify(course_data)
        else:
            return jsonify({"error": "Course not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'

    # 需要设置 SESSION_COOKIE_HTTPONLY 为 False
    app.config['SESSION_COOKIE_HTTPONLY'] = False

    Session(app)
    app.run()
