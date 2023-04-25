import sqlite3
import pandas as pd
import openpyxl
from sql_execute import *

# data = pd.read_excel('base.xlsm', sheet_name='ОСНОВНАЯ')
# data = data[['Наименование сценария', 'Домен']]
workbook = openpyxl.load_workbook('main_table.xlsx')
worksheet = workbook['ОСНОВНАЯ']

conn = sqlite3.connect('base.db')
cur = conn.cursor()


def new_table():
    cur.execute(create_table)
    # cur.execute(add_test)

    for row in worksheet.iter_rows(min_row=2, values_only=True):
        cur.execute(insert_table, row)


def get_columns_with_filter(where, columns=None, order=None):
    # устанавливаем соединение с БД
    # формируем запрос SQL
    # columns = ['name', 'domen', 'technology', 'metod', 'func_group']
    _flag = False
    if columns is None:
        _flag = True
        columns = ['name']

    query = f"SELECT {', '.join(columns)} FROM projects WHERE "

    flag = False
    for key, value in where.items():
        if value:
            query += f"{key}='{value}' AND "
            flag = True
    if flag:
        query = query[:-4]
    else:
        query = query[:-7]

    # if where:
    #     sql += " WHERE " + " AND ".join(f"{k} = ?" for k in where.keys())

    if order and order in columns:
        query += f" ORDER BY {order}"
    else:
        query += f" ORDER BY {columns[0]}"

    # выполняем запрос и получаем результат
    cur.execute(query)
    results = cur.fetchall()

    # закрываем соединение с БД
    # cur.close()
    # conn.close()

    # возвращаем результат
    if _flag:
        return [result[0] for result in results]
    else:
        return results

def get_list_of_categories(order, where):
    # conn = sqlite3.connect('database.db')
    # cursor = conn.cursor()

    query = f"SELECT DISTINCT {order} FROM projects WHERE "
    flag = False
    for key, value in where.items():
        if value:
            query += f"{key}='{value}' AND "
            flag = True
    if flag:
        query = query[:-4]
    else:
        query = query[:-7]

    query += f' ORDER BY {order}'
    cur.execute(query)
    results = cur.fetchall()

    # cursor.close()
    # conn.close()

    return [result[0] for result in results]

# cur.execute(test_tech)
#
# ans = cur.fetchone()

# order = 'domen'
#
# where = {
#     'func_group': 'Корпоративные функции'
# }
#
# # print(get_columns_with_filter(order, where))
# print(get_list_of_categories(order, where))

# for column in ans:
#     print('_' * 50)
#     for i in ans:
#         for j in i:
#             print(j, '|  ', end='')
#         print('\n', '-' * 50, sep='')
conn.commit()
A = 1

