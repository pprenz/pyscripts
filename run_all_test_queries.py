import pyodbc
import sys
import datetime

def prettify(val):
    if val == None:
        return "Null"
    elif type(val) == bool:
        return "%s" % ("1" if True else "0")
    elif type(val) == int:
        return "%s" % val
    elif type(val) == float:
        return "%s" % val
    elif type(val) == str:
        return "'%s'" % val
    elif type(val) == datetime:
        return "'%s'" % val.strftime("%Y-%m-%d %H:%M")
    else:
        return "'%s'" % val

connection_string = "DSN=so1web;UID=sof1;PWD=dbAdmin@so1"
#connection_string = "DSN=so1scheduler-prod;UID=sof1;PWD=dbAdmin@so1"
#connection_string = "SERVER=10.1.215.101;UID=sof1;PWD=dbAdmin@so1;DRIVER={SQL Server}"

schema_name = 'dit'
sql_get_all_dit_views = '''
SELECT 
    Type = TABLE_TYPE, 
    Owner = TABLE_SCHEMA, 
    Name = TABLE_NAME
FROM 
    INFORMATION_SCHEMA.TABLES 
WHERE 
    TABLE_TYPE IN ('VIEW') 
AND TABLE_SCHEMA = '%s'
ORDER BY 
    TABLE_TYPE, 
    TABLE_SCHEMA, 
    TABLE_NAME
''' % schema_name

connection = pyodbc.connect(connection_string, autocommit=True)
cursor = connection.cursor()

cursor.execute(sql_get_all_dit_views)
views = cursor.fetchall()
n_failures = 0

# Run all the DIT Tests: The DIT Tests fail if the View returns any rows back
print "Running DATA INTEGRITY TESTS"
for view in views:
    print ("Testing %s..." % view.Name),  # comma suppresses newline
    sys.stdout.flush()
    startTime = datetime.datetime.now()
    cursor.execute("select * from %s.%s" % (schema_name, view.Name))
    rows = cursor.fetchall()
    endTime = datetime.datetime.now()
    runTime = endTime - startTime
    if rows:
        n_failures += 1
        print "[FAILED]"
        print "  --" + ",".join(map(lambda col: str(col[0]), cursor.description))
        print "  " + "\n  ".join(map(lambda row: ",".join(map(prettify, row)), rows))
        print
    else:
        print "[ok]. Run Time:", runTime.seconds, "Seconds", runTime.microseconds, "MicroSeconds"

cursor.close()

if n_failures == 0:
    print "All Data Integrity Tests passed !"
else:
    print "%d Data Integrity Tests failed!" % n_failures

# Data Quality Tests
schema_name = 'DQT'
sql_get_all_dqt_views = '''
SELECT 
    Type = TABLE_TYPE, 
    Owner = TABLE_SCHEMA, 
    Name = TABLE_NAME
FROM 
    INFORMATION_SCHEMA.TABLES 
WHERE 
    TABLE_TYPE IN ('VIEW') 
AND TABLE_SCHEMA = '%s'
ORDER BY 
    TABLE_TYPE, 
    TABLE_SCHEMA, 
    TABLE_NAME
''' % schema_name

connection = pyodbc.connect(connection_string, autocommit=True)
cursor = connection.cursor()

cursor.execute(sql_get_all_dqt_views)
dqtviews = cursor.fetchall()

print "Running DATA QUALITY TESTS"
for view in dqtviews:
    print ("Testing %s.%s..." % (schema_name, view.Name)),  # comma suppresses newline
    sys.stdout.flush()
    cursor.execute("select * from %s.%s" % (schema_name, view.Name))
    dqtrows = cursor.fetchall()

    if dqtrows:
        print "[OUTPUT]"
        print "  --" + "\t".join(map(lambda col: str(col[0]), cursor.description))
        print "  " + "\n  ".join(map(lambda row: "\t".join(map(prettify, row)), dqtrows))
        print
cursor.close()

sys.exit(n_failures)
