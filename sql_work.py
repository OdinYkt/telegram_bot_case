import sqlite3
import pandas as pd
from sql_execute import *

data = pd.read_excel('base.xlsm', sheet_name='ОСНОВНАЯ')
data = data[['Наименование сценария', 'Домен']]

conn = sqlite3.connect('base.db')
cur = conn.cursor()

cur.execute(create_new)
cur.execute(add_test)
conn.commit()
A = 1

