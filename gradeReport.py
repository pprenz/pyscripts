'''
Grade Report

$Source$
$Revision$
$Author$
$Date$

This process gets the Grade Report for the given set of parameters

'''
import os
import csv
import sys
import pyodbc
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders

#connection_string = "DSN=so1web;UID=sof1;PWD=dbAdmin@so1;DRIVER={SQL Server}"
connection_string = "DSN=so1scheduler-prod;UID=sof1;PWD=dbAdmin@so1;DRIVER={SQL Server}"

#==============================================================================
# Exceptions
#==============================================================================
class GradeReportException(Exception): pass

#==============================================================================
# GradeReport
#==============================================================================
class GradeReport:
    """
    Obtains and emails the grade Report query
    """
    #--------------------------------------------------------------------------
    def __init__(self, startDate, endDate, schoolID):
        """
        Intialize the class
        """
        self.startDate = startDate
        self.endDate   = endDate
        self.schoolID  = schoolID

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
        msg['Subject'] = "Grade Report"
        body = '''The Grade Report for the following Parameters is attached
        School ID: %s
        Start Date: %s
        End Date: %s
        ''' % (self.schoolID, self.startDate, self.endDate)
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
            with TotalSkillPoints as
            (
                select r.StudentId,
                       sum(r.Points) as TotalPoints
                from (
                    select    s.StudentId,
                            case
                            when ar.result >= 4 then sk.Par * (ar.result / 5.0)
                            else 0
                            end as Points
                    from dbo.Students s
                    left join Assessment.FilteredAssessmentResults ar on ar.StudentId = s.StudentId
                    left join dbo.Assessments a on a.AssessmentId = ar.AssessmentId
                    left join dbo.Skills sk on sk.SkillId = a.SkillId
                where ar.AssessmentDate between '%s' and '%s'
                ) r
                group by r.StudentId
            ),
            QualifiedExposures as
            (
                select ss.StudentId,
                        COUNT(*) as Total
                from portal.QualifiedStudentSchedules ss
                where ss.ScheduledDate between '%s' and '%s'
                group by ss.StudentId
            ),
            GradeAverages as
            (
                select StudentId,
                count(r.ParticipationGrade) as NumParticipationGrades,
                count(r.ClassworkGrade) as NumClassworkGrades,
                count(r.HomeworkGrade) as NumHomeworkGrades,
                ROUND(AVG(CAST(r.ParticipationGrade as float)), 1) AvgParticipation,
                ROUND(AVG(CAST(r.ClassworkGrade as float)), 1) AvgClasswork,
                ROUND(AVG(CAST(r.HomeworkGrade as float)), 1) AvgHomework
                from --this subquery uses distinct to filter out dupes
                (
                    select distinct
                    ScheduledStudentId,
                    ScheduledLessonId,
                    StudentId,
                    ScheduledDate,
                    SchoolPeriodId,
                    ParticipationGrade,
                    ClassworkGrade,
                    HomeworkGrade,
                    MarkingPeriodNumber
                    from portal.StudentSchedule
                ) r
                where r.ScheduledDate between '%s' and '%s'
                group by r.StudentId
            )
            select  sch.Name as School,
                    schs.SchoolSectionCode as Section,
                    stu.StudentId,
                    stu.FirstName,
                    stu.LastName,
                    sg.NumParticipationGrades,
                    sg.AvgParticipation as ParticipationAverage,
                    sg.NumClassworkGrades,
                    sg.AvgClasswork as ClassworkAverage,
                    sg.NumHomeworkGrades,
                    sg.AvgHomework as HomeworkAverage,
                    tsp.TotalPoints as SkillPoints,
                    qe.Total as QualifiedExposures
            from ActiveStudents stu
            join Schools sch on sch.SchoolId = stu.SchoolId
            join StudentSections stus on stus.StudentId = stu.StudentId
            join SchoolSections schs on schs.SchoolSectionId = stus.SchoolSectionId
            join GradeAverages sg on sg.StudentId = stu.StudentId
            join TotalSkillPoints tsp on tsp.StudentId = stu.StudentId
            join QualifiedExposures qe on qe.StudentId = stu.StudentId
            where sch.SchoolId = %s
            order by School, Section, StudentId
            ''' %(self.startDate, self.endDate, self.startDate, self.endDate, self.startDate, self.endDate, self.schoolID)
            cursor.execute(query)
            self.gradeReportsTuple = cursor.fetchall()
            self.fileName = 'grade_report.csv'
            f = open(self.fileName, 'wb')
            writer = csv.writer(f)
            writer.writerow(["School","Section","StudentId","FirstName","LastName","NumParticipationGrades","ParticipationAverage","NumClassworkGrades","ClassworkAverage","NumHomeworkGrades","HomeworkAverage","SkillPoints","QualifiedExposures"])
            for resultTuple in self.gradeReportsTuple:
                writer.writerow(resultTuple)
            f.seek(0)
            f.close()
            # Send an email
            self.sendEmail()
        except Exception, e:
            raise GradeReportException("[runReport] Could not run Grade Report %s " %e)        

#------------------------------------------------------------------------------
# Script Entry Point
#------------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        startDate = sys.argv[1]
        endDate   = sys.argv[2]
        schoolID  = sys.argv[3]
    except IndexError, e:
        raise GradeReportException("No arguments Specified. Please give the startDate and EndDate as arguments")
    g = GradeReport(startDate, endDate, schoolID)
    g.runReport()
