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

def get_list_of_categories(order, where):
    # устанавливаем соединение с БД
    # формируем запрос SQL
    columns = ['name', 'domen', 'technology', 'metod', 'func_group']
    sql = f"SELECT {', '.join(columns)} FROM projects"

    if where:
        sql += " WHERE " + " AND ".join(f"{k} = ?" for k in where.keys())

    if order in columns:
        sql += f" ORDER BY {order}"
    else:
        sql += f" ORDER BY {columns[0]}"

    # выполняем запрос и получаем результат
    cur.execute(sql, tuple(where.values()))
    result = cur.fetchall()

    # закрываем соединение с БД
    # cur.close()
    # conn.close()

    # возвращаем результат
    return result

# cur.execute(test_tech)
#
# ans = cur.fetchone()

# order = 'domen'
#
# where = {
#     'technology': 'VR',
#     'metod': 'Обучение и тестирование персонала'
# }
#
# print(get_list_of_categories(order, where))
# # for column in ans:
# #     print('_' * 50)
# #     for i in ans:
# #         for j in i:
# #             print(j, '|  ', end='')
# #         print('\n', '-' * 50, sep='')
# conn.commit()
# A = 1

