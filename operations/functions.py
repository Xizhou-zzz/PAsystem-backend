from operations.controller import DBcontroller

db = DBcontroller.Database()


def check(username, password):
    saved_message = db.select('users', condition=f"username = '{username}'")  # 查询数据库信息
    if saved_message.empty:
        print(f"没有找到 {username} 的信息")
        return 0, None
    else:
        saved_password = saved_message['password'].iloc[0]
        print(f"密码正确？{saved_password == password}")
        if saved_password == password:
            valid = 1
            access = saved_message['access'].iloc[0]
        else:
            valid = 0
            access = 'err'
        return valid, access


def get_evaluations(username):
    return username


def get_data():
    # 在这里实现从后端数据库或其他数据源获取数据的逻辑
    # 返回获取到的数据
    data = [
        {
            'key': '1',
            'homework_title': '作业1',
            'course_id': 'C001',
            'class_id': 'CL001',
            'student_name': '学生A',
            'grade': '85',
            'peer_reviewer': '学生B'
        },
        # 更多数据...
    ]
    return data


def create_peer_table(usernames):
    return None