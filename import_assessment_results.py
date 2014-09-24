import pyodbc
import csv

connection_string = "DSN=so1web;UID=sof1;PWD=dbAdmin@so1"
#connection_string = "SERVER=10.1.215.101;UID=sof1;PWD=dbAdmin@so1;DRIVER={SQL Server}"
connection = pyodbc.connect(connection_string, autocommit=True)
cursor = connection.cursor()

cursor.execute("truncate table scrap.LatestRawAssessmentResults")
cursor.execute("""
    BULK INSERT scrap.LatestRawAssessmentResults
           FROM 'j:/aspire/master.csv'
           WITH
             (
                FIRSTROW = 2,
                FIELDTERMINATOR = ',',
                ROWTERMINATOR = '\n'
             )
""")
n_rows = cursor.rowcount
cursor.close()

print "Imported %d rows." % n_rows
