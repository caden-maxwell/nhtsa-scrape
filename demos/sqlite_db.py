# Simple example of SQLite3 utilization

import sqlite3

connection = sqlite3.connect("demos/cases.db")
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS cases(caseid, casenum, vehnum, year, make, model)")

cursor.execute("""
    INSERT INTO cases VALUES
        (1342243, 1, 1, 2015, 'Ford', 'F150'),
        (2125234, 1, 2, 2013, 'Ford', 'F250'),
        (1023952, 2, 1, 2019, 'Ford', 'F350')
""")

result = cursor.execute("SELECT * FROM cases")
lst = result.fetchall()
print("caseid casenum vehnum year make model")
for row in lst:
    for item in row:
        print(item, end=" ")
    print()
    
cursor.execute("DELETE FROM cases")

connection.commit()
connection.close()