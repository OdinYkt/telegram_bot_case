create_new = """CREATE TABLE IF NOT EXISTS projects(
   project_id INTEGER PRIMARY KEY AUTOINCREMENT ,
   name TEXT,
   domen TEXT);
"""
add_test = """INSERT INTO projects(
'name', 'domen')
VALUES ('test1', 'test2')
"""