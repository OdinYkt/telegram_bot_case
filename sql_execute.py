create_new = """CREATE TABLE IF NOT EXISTS projects(
   project_id INTEGER PRIMARY KEY AUTOINCREMENT ,
   name TEXT,
   domen TEXT);
"""
add_test = """INSERT INTO projects(
'name', 'domen')
VALUES ('test1', 'test2')
"""

create_table = """CREATE TABLE IF NOT EXISTS projects (
                      project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        description TEXT,
                        domen TEXT,
                        technology TEXT,
                        metod TEXT,
                        func_group TEXT,
                        potencial_rate INTEGER,
                        potencial_dec TEXT,
                        market_rate INTEGER,
                        market_mat TEXT,
                        readiness_rate INTEGER,
                        readiness TEXT,
                        implementation TEXT,
                        Benchmarking TEXT,
                        Benchmarking_description TEXT,
                        Benchmarking_company TEXT,
                        name_project_gpn TEXT,
                        description_project TEXT,
                        name_project  TEXT
                    )"""