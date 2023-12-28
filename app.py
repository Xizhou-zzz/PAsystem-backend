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

@app.route('/api/sendcode', methods=['POST'])
def send_code():
    data = request.json
    email = data['email']
    # check if email exists in the database
    conn = mysql.connector.connect(host='localhost', user='root', password='124356tbw', database='pa') # 修改为自己的数据库连接信息
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
    result = cursor.fetchall()
    if len(result) == 0:
        return jsonify({'message': '该邮箱未注册'}), 400
    # generate code and store it in the cache
    code = str(random.randint(100000, 999999))
    code = "123456"  # 压力测试用
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
    conn = mysql.connector.connect(host='localhost', user='root', password='124356tbw', database='pa')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', (email,))      # check if email exists in the database
    result = cursor.fetchall()
    if len(result) == 0:
        return jsonify({'message': '该邮箱未注册'}), 400
    # check if the code is correct
    # get the code from redis or other caching service
    correct_code = code_cache.get(email)
    print("code:" + code)
    print("correct_code:" + str(correct_code))
    # if correct_code is None:
    #     return jsonify({'message': '验证码过期或不存在'}), 400
    # if code != correct_code:
    #     return jsonify({'message': '验证码错误'}), 400
    # login success
    return jsonify({'message': '登录成功', 'user': {'id': result[0][0], 'username': result[0][1], 'access': result[0][3]}}), 200

@app.route('/api/safetysettings/updatepassword', methods=['PUT'])
def update_password():
    data = request.json
    username = data['username']
    current_password = data['currentPassword']
    new_password = data['newPassword']

    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='Ys012567', database='pa')
        cursor = conn.cursor()

        # 获取当前用户的密码
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        stored_password = cursor.fetchone()[0]
        print(stored_password)
        print(current_password)
        # 验证当前密码
        if not stored_password == current_password:
            return jsonify({'error': 'Current password is incorrect'}), 401

        # 更新密码
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
        conn.commit()

        return jsonify({'message': 'Password updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


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
        password='124356tbw',
        database='pa'
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM course')
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    print(jsonify(courses))
    return jsonify(courses)


@app.route('/api/user/<user_name>', methods=['GET'])
def get_user(user_name):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='124356tbw',
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
            password='124356tbw',
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

@app.route('/api/addcourse', methods=['POST'])
def add_course():
    data = request.json
    course_name = data['courseName']
    course_id = data['courseId']
    main_teacher = data['mainTeacher']
    teaching_classroom = data['teachingClassrom']
    teaching_time = data['teachingTime']

    # 连接数据库并执行插入操作
    conn = mysql.connector.connect(host='localhost', user='root', password='Ys012567', database='pa')
    cursor = conn.cursor()

    try:
        query = "INSERT INTO course (course_name, course_id, main_teacher, teaching_room, teaching_time) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (course_name, course_id, main_teacher, teaching_classroom, teaching_time))
        conn.commit()
        return jsonify({'message': 'Course added successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

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
            password='124356tbw',
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
            password='124356tbw',
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
            password='124356tbw',
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
    username = "teacher1"
    session_info = session.get(username)  # 从前端中获取当前登录用户的用户名
    print(f'homework_platform-get: sesion_info: {session_info}')
    homework_data = functions.get_homework_data('teacher1')
    return jsonify(homework_data)

# @app.route('/homework_platform/homework_manage/create', methods=['POST'])
# def create_homework():
    # teacher_name = session.get('username')  # 从前端中获取当前登录用户的用户名
    # print(f"{teacher_name} -- request to create homework")
    # homework_data = request.json  # 从请求的 JSON 数据中获取作业信息
    # status = functions.insert_homework(homework_data, teacher_name)
    # if status:
    #     return jsonify({'status': 'success', 'message': '作业已创建'})
    # else:
    #     return jsonify({'status': 'failure', 'message': 'create failed.'})


@app.route('/Course_platform_t/Student_grade/delete', methods=['DELETE'])
def grade_delete():
    return True


# @app.route('/Homework_platform/homework_manage/add', methods=['POST'])
# def add_homework():
#     data = request.json
#     status = functions.add_homework(data)
#     if status:
#         return jsonify({'status': 'success', 'message': 'Homework added successfully.'})
#     else:
#         return jsonify({'status': 'failure', 'message': 'adding homework failed.'})


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


@app.route('/api/course_manage/deletecourse/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='Ys012567', database='pa')
        cursor = conn.cursor()

        # 删除课程
        cursor.execute("DELETE FROM course WHERE course_id = %s", (course_id,))
        conn.commit()

        return jsonify({'message': 'Course deleted successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/course_manage/editcourse/<course_id>', methods=['PUT'])
def edit_course(course_id):
    data = request.json
    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='Ys012567', database='pa')
        cursor = conn.cursor()

        # 更新课程信息
        cursor.execute("UPDATE course SET course_name = %s, main_teacher = %s, teaching_room = %s, teaching_time = %s WHERE course_id = %s",
                      (data['course_name'], data['main_teacher'], data['teaching_room'], data['teaching_time'], course_id))
        conn.commit()

        return jsonify({'message': 'Course updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/people_management/get_student_courses/<student_id>', methods=['GET'])
def get_student_courses(student_id):
    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='Ys012567', database='pa')
        cursor = conn.cursor()

        query = """
        SELECT course.course_name 
        FROM teacher_student_class 
        JOIN course ON teacher_student_class.course_id = course.course_id 
        WHERE teacher_student_class.student_id = %s
        """
        cursor.execute(query, (student_id,))
        courses = cursor.fetchall()

        return jsonify({'courses': [course[0] for course in courses]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/people_management/get_all_courses', methods=['GET'])
def get_all_courses():
    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='YourPassword', database='pa')
        cursor = conn.cursor()

        query = "SELECT course_name FROM course"
        cursor.execute(query)
        courses = cursor.fetchall()

        return jsonify({'courses': [course[0] for course in courses]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/homework_manage/addhomework/<user_name>', methods=['POST'])
def add_homework(user_name):
    data = request.json
    course_name = data['courseName']
    title = data['title']
    due_date = data['dueDate']
    description = data['description']

    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='Ys012567', database='pa')
        cursor = conn.cursor()

        # 获取教师ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (user_name,))
        teacher_id = cursor.fetchone()[0]

        # 获取course_id和class_id
        cursor.execute(
            "SELECT DISTINCT course.course_id, class_id FROM teacher_student_class, course WHERE teacher_id = %s AND course.course_id = teacher_student_class.course_id AND course.course_name = %s",
            (teacher_id, course_name))
        result = cursor.fetchone()
        if result:
            course_id, class_id = result

            # 插入homework表
            query = "INSERT INTO homework (class_code, course_name, title, due_date, assignment_description, teacher_id, course_code) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (class_id, course_name, title, due_date, description, teacher_id, course_id,))
            conn.commit()

            # 获取homework_id
            homework_id = cursor.lastrowid

            # 获取所有相关学生ID
            cursor.execute("SELECT student_id FROM teacher_student_class WHERE class_id = %s", (class_id,))
            student_ids = cursor.fetchall()

            # 为每个学生插入记录
            query = "INSERT INTO student_homework (student_id, teacher_id, course_id, class_id, homework_id, do_state, correction_state, grade) VALUES (%s, %s, %s, %s, %s, 'False', 'False', '-1')"
            for student_id in student_ids:
                cursor.execute(query, (student_id[0], teacher_id, course_id, class_id, homework_id,))
            conn.commit()
            return jsonify({'message': 'Homework added successfully'}), 200
        else:
            return jsonify({'error': 'Unable to find course or class ID'}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/homework_manage/deletehomework/<course_name>/<title>', methods=['DELETE'])
def delete_homework(course_name, title):
    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='Ys012567', database='pa')
        cursor = conn.cursor()

        # 删除 student_homework 表中的记录
        cursor.execute(
            "DELETE FROM student_homework WHERE homework_id IN (SELECT hid FROM homework WHERE course_name = %s AND title = %s)",
            (course_name, title))

        # 删除 homework 表中的记录
        cursor.execute("DELETE FROM homework WHERE course_name = %s AND title = %s", (course_name, title))

        conn.commit()
        return jsonify({'message': 'Homework deleted successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/course_platform_t/student_grade/getStudent/<user_name>', methods=['GET'])
def get_grades(user_name):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teacher_student_class,users,homework,course WHERE users.id = teacher_student_class.teacher_id AND users.username = %s AND homework.class_code = teacher_student_class.class_id AND course.course_id = teacher_student_class.course_id" ,(user_name,))
        grades_data = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(grades_data)
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
        cursor.execute("SELECT * FROM course,teacher_student_class,users WHERE users.username = %s and teacher_student_class.course_id = course.course_id AND users.id = teacher_student_class.student_id", (user_name,))
        course_data = cursor.fetchall()
        cursor.close()
        connection.close()
        if course_data:
            return jsonify(course_data)
        else:
            return jsonify({"error": "Course not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/course_platform_s/mission/gethomework/<user_name>', methods=['GET'])
def get_homework(user_name):
    # 连接数据库并查询数据
    conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student_homework,users,homework WHERE homework.course_code = student_homework.course_id AND users.username = %s AND users.id = student_homework.student_id AND homework.hid = student_homework.homework_id", (user_name,))
    homeworks = cursor.fetchall()
    cursor.close()
    conn.close()

    # 格式化数据并返回
    return jsonify(homeworks)

@app.route('/api/course_platform_s/mission/getmission/<user_name>', methods=['GET'])
def get_mission(user_name):
    # 连接数据库并查询数据
    conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ys012567',
            database='pa'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mission")
    missions = cursor.fetchall()
    conn.close()

    # 格式化数据并返回
    return jsonify(missions)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'

    # 需要设置 SESSION_COOKIE_HTTPONLY 为 False
    app.config['SESSION_COOKIE_HTTPONLY'] = False

    Session(app)
    app.run()
