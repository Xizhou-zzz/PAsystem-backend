import random
import time
import pymysql.err

from operations.controller import DBcontroller

# from controller import DBcontroller     # 单独调试函数时使用
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
            valid = -1
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
            'grade': '90',
            'peer_reviewer': '学生B'
        },
        # 更多数据...
    ]
    return data


def get_course_data():
    df = db.select('course')
    course_data = []

    for index, row in df.iterrows():
        course = {
            'key': str(index + 1),
            'course_name': row['course_name'],
            'course_id': row['course_id'],
            'teacher_name': row['main_teacher'],
            'classroom': row['teaching_room'],
            'time': row['teaching_time'],
        }
        course_data.append(course)

    return course_data


def course_ins(data):
    try:
        db.insert("course", tuple(data.values()))
        return True
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:  # 检查错误码是否为 1062, 有关主键的冲突问题
            print("Duplicate entry. Insertion failed.")
        else:
            # 其他处理逻辑
            print("An error occurred during insertion:", e)


# def course_del(course_id):
#     condition = f"course_id='{course_id}'"
#     db.delete("course", condition)
#     return True

def course_del(course_id):
    condition = f"course_id='{course_id}'"

    # 使用select方法查询指定的course_id
    existing_courses = db.select("course", condition=condition)

    # 检查DataFrame是否为空（即是否找到了匹配的课程）
    if not existing_courses.empty:
        # 如果DataFrame不为空，说明找到了课程，执行删除操作
        db.delete("course", condition)
        return True
    else:
        # 如果DataFrame为空，说明没有找到对应的课程，返回False
        return False


# operation将包括增（ins）删（del）改（upd）查（sl）, 被操作的表名为course
# def course_management(operation):
#     data = {
#         "course_name": "软件项目管理与产品运维",
#         "course_id": "M310008B",
#         "main_teacher": "马翼萱",
#         "teaching_room": "YF509",
#         "teaching_time": "Mon 16:20-18:10"
#     }
#     if operation == "ins":
#         try:
#             db.insert("course", tuple(data.values()))
#         except pymysql.err.IntegrityError as e:
#             if e.args[0] == 1062:  # 检查错误码是否为 1062, 有关主键的冲突问题
#                 print("Duplicate entry. Insertion failed.")
#             else:
#                 # 其他处理逻辑
#                 print("An error occurred during insertion:", e)
#     elif operation == "del":
#         condition = f"course_id='{data['course_id']}'"
#         db.delete("course", condition)
#     elif operation == "upd":
#         column_values = ", ".join([f"{k}='{v}'" for k, v in data.items()])
#         condition = f"course_id='{data['course_id']}'"
#         db.update("course", column_values, condition)
#     # elif operation == "sl":


def create_peer_table(usernames, homework):
    # 静态数据：要求前端返回交作业的学生列表 以及 该作业的名称与布置时间（精确到日，格式以下划线隔开）
    usernames = {
        "usernames": ["student1", "student2", "student3", "student4", "student5", "student6"]
    }
    homework = {
        "name": "computer_network",
        "date": "2021_11_23"
    }
    students_list = usernames["usernames"]
    num_students = len(students_list)
    print(f"num_students:{num_students}")
    if num_students < 3:
        print("完成学生数量过少")
        return None  # 直接跳出函数
    else:
        # 确定每个人的工作量，至少为3
        min_reviews_float = max(
            num_students / 6 if num_students < 30 else num_students / 8 if num_students < 70 else num_students / 10, 3)
        min_reviews = int(min_reviews_float)
    print(f"每人最少评：{min_reviews}份")

    homework_name = homework["name"]
    homework_date = homework["date"]
    table_name = "pt_" + homework_name + "_" + homework_date  # 创建的互评表的表名，格式为pt_课程名_日期
    print(table_name)
    columns = "reviewer VARCHAR(50) NOT NULL, reviewee VARCHAR(50) NOT NULL"
    db.create_table(table_name, columns)

    # 生成表格
    for i in range(num_students * min_reviews):
        # 随机选择评选人
        reviewer = random.choice(students_list)
        # 随机选择被评选人
        # 确保生成的评选对中包含所有学生
        # 可以先选择剩下还没被选择的学生里面的一个，然后再从已经选择的评选对中随机选择一个作为被评选人
        candidates = [x for x in students_list if x != reviewer]  # 这两行代码我只能说 W T F !!!!!!
        reviewee = random.choice(candidates)
        db.insert(table_name, (reviewer, reviewee))

    df = db.select(table_name)
    # 返回尚不完善
    return table_name


def add_homework(data):
    if data:
        return True
    else:
        return False


def submit_homework(data):
    if data:
        return True
    else:
        return False


def generate_report(data):
    if data:
        return True
    else:
        return False


##################
# 分割线  teacher #
##################
def insert_homework(homework_data, teacher_name):
    # 构造表名
    table_name = f'{teacher_name}_homework'
    try:
        db.insert(table_name, tuple(homework_data.values()))
        return True
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:  # 检查错误码是否为 1062, 有关主键的冲突问题
            print("Duplicate entry. Insertion failed.")
        else:
            # 其他处理逻辑
            print("An error occurred during insertion:", e)


def get_homework_data(teacher_name):
    table_name = f'{teacher_name}_homework'
    df = db.select(table_name)
    print(df)
    homework_data = []

    for index, row in df.iterrows():
        homework = {
            'key': str(index + 1),
            'homework_title': row['title'],
            'course_id': row['course_code'],
            'class_id': row['class_code'],
            'submitted_count': row['submitted_count'],
            'total_count': row['total_count'],
            'course_name': row['course_name'],
            'deadline': row['due_date'],
            'assignment_description': row['assignment_description'],
            'attachment_path': row['attachment_path']
        }
        homework_data.append(homework)

    return homework_data

