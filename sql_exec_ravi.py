import pyodbc
import sys
import os

connection_string = "DSN=so1scheduler;UID=sof1;PWD=dbAdmin@so1;DRIVER={SQL Server}"


stored_proc_name = sys.argv[1]
try:
    connection = pyodbc.connect(connection_string, autocommit=True)
    cursor = connection.cursor()

    cursor.execute("exec %s" % stored_proc_name)
    rows = cursor.fetchall()
    print rows
    cursor.close()

    for row in rows:
        print ",".join(map(str,row))
except Exception as e:
    print "Encountered an SQL Exception", e
    sys.exit(1)
    
sys.exit(0 if len(rows) == 0 else 1)
