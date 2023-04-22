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

cur.execute(create_table)
# cur.execute(add_test)

for row in worksheet.iter_rows(min_row=2, values_only=True):
    cur.execute (
        ''' INSERT INTO projects ( name,
                        description,
                        domen,
                        technology,
                        metod,
                        func_group,
                        potencial_dec,
                        potencial_rate,
                        market_rate,
                        market_mat,
                        readiness_rate,
                        readiness,
                        implementation,
                        Benchmarking,
                        Benchmarking_description,
                        Benchmarking_company,
                        name_project_gpn,
                        description_project,
                        name_project)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', row)

conn.commit()
A = 1

