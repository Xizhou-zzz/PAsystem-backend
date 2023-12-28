import pandas as pd
import pymysql


class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="124356tbw",
            database="pa"
        )
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        # 判断表格是否存在
        self.cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if self.cursor.fetchone():
            # 如果表格已经存在，则删除它
            self.cursor.execute(f"DROP TABLE {table_name}")
            print(f"Table {table_name} deleted.")

        # 创建表格
        sql = f"CREATE TABLE {table_name} ({columns})"
        self.cursor.execute(sql)
        self.conn.commit()
        print(f"Table {table_name} created.")

    def insert(self, table_name, values):
        # 插入数据
        placeholders = ', '.join(['%s' for _ in values])
        sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.cursor.execute(sql, values)
        self.conn.commit()
        print("Record inserted successfully.")

    def update(self, table_name, column, value, condition):
        # 更新数据
        sql = f"UPDATE {table_name} SET {column}=%s WHERE {condition}"
        self.cursor.execute(sql, (value,))
        self.conn.commit()
        print("Record updated successfully.")

    def delete(self, table_name, condition):
        # 删除数据
        sql = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(sql)
        self.conn.commit()
        print("Record deleted successfully.")

    def select(self, table_name, columns="*", condition=None):
        # 查询数据
        if condition:
            sql = f"SELECT {columns} FROM {table_name} WHERE {condition}"
        else:
            sql = f"SELECT {columns} FROM {table_name}"

        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        df = pd.DataFrame(results, columns=[desc[0] for desc in self.cursor.description])
        return df

    def close(self):
        # 关闭数据库连接
        self.cursor.close()
        self.conn.close()
        print("Database connection closed.")


# # 使用示例
# db = Database()
#
# # 创建表格
# db.create_table('employees', 'id INTEGER PRIMARY KEY, name VARCHAR(100), age INTEGER')
#
# # 插入数据
# db.insert('employees', (1, 'John', 25))
# db.insert('employees', (2, 'Alice', 30))
# db.insert('employees', (3, 'Bob', 35))
#
# # 更新数据
# db.update('employees', 'age', 26, 'id=1')
#
# # 删除数据
# db.delete('employees', 'id=3')
#
# df = db.select('employees', condition='age>25')
# # 打印 DataFrame
# print(df)
#
# # 可以像操作 DataFrame 一样对查询结果进行处理
# # 例如，筛选年龄大于30的员工
# filtered_df = df[df['age'] > 30]
# print(filtered_df)
#
# # 关闭连接
# db.close()
