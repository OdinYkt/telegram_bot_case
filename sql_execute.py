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

insert_table = ''' INSERT INTO projects ( name,
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
        '''

test_tech = """SELECT name, metod FROM projects WHERE technology = 'VR'"""