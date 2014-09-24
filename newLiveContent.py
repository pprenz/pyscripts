'''
Newly Scheduled Live Content

$Source$
$Revision$
$Author$
$Date$

This process gets the list of newsly scheduled Content Data and sends an email to Adam Reingold
'''
import csv
import os
import datetime
import pyodbc
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders

connection_string = "DSN=so1scheduler;UID=sof1;PWD=dbAdmin@so1;DRIVER={SQL Server}"

#==============================================================================
# Exceptions
#==============================================================================
class newLiveContentException(Exception): pass

#==============================================================================
# GradeReport
#==============================================================================
class NewLiveContent:
    """
    Obtains and emails the newly scheduled Live Content data
    """
    #--------------------------------------------------------------------------
    def __init__(self):
        """
        Intialize the class
        """
    #--------------------------------------------------------------------------
    def sendEmail(self):
        """
        Send an e-mail notification with the details
        """
        msg = MIMEMultipart()
        source = "hudson@so1live.com"
        msg['From'] = source

        dest = 'ravichandra.devineni@gmail.com'
        msg['To'] = dest
        msg['Subject'] = "Newly Scheduled Live Content %s"  %datetime.date.today().strftime("%m/%d/%Y")
        body = '''Newly Scheduled Live Content attached
        '''
        msg.attach(MIMEText(body))

        # Attachments
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(self.fileName,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment;filename="%s"' % os.path.basename(self.fileName))
        msg.attach(part)

        # The actual mail send
        server = smtplib.SMTP('localhost')
        server.sendmail(source, dest, msg.as_string())
        server.quit()    
    #--------------------------------------------------------------------------
    def runReport(self):
        '''
        This is the main function in this program which serves as a 
        calling function to other sub-functions
        '''
        try:
            connection = pyodbc.connect(connection_string, autocommit=True)
            cursor = connection.cursor()
            query = '''
            select ls.VendorLessonID,
                   ls.PICode,
                   ls.Modality,
                   COUNT(distinct StudentId)as students 
            from LatestSchedules ls
            where ModalityClassId in (1,2)
	          and LessonId not in (select distinct LessonId 
                                   from Schedules 
                                   where ScheduledDate < ls.ScheduledDate
                                  )
            group by ls.VendorLessonID, ls.PICode, ls.Modality 
            '''
            cursor.execute(query)
            self.liveContentTuple = cursor.fetchall()
            self.fileName = 'live_contentreport.csv'
            f = open(self.fileName, 'wb')
            writer = csv.writer(f)
            writer.writerow(["VendorLessonID", "PICode", "Modality", "Students"])
            for resultTuple in self.liveContentTuple:
                writer.writerow(resultTuple)
            f.seek(0)
            f.close()
            # Send an email
            self.sendEmail()
        except Exception, e:
            raise newLiveContentException("[runReport] Could not live content  Grade Report %s " %e)        

#------------------------------------------------------------------------------
# Script Entry Point
#------------------------------------------------------------------------------
if __name__ == '__main__':
    n = NewLiveContent()
    n.runReport()
