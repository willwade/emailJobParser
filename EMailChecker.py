import EMailDownloader
import EMailSqlDump
import MySQLdb
import datetime
import dateutil.parser
import dateutil.tz
import cPickle
import os
import NHS_JOBS_CONSTANTS as N

def downloadAvailableEMails():
    tableName = N.JOBS_DETAIL_TABLENAME
    startDate = datetime.datetime(2000,1,1, tzinfo = dateutil.tz.tzoffset(None,0))
    connection = MySQLdb.connect(host=N.SQL_HOST_NAME,user=N.SQL_USER_NAME,passwd=N.SQL_PASSWD,db=N.SQL_DB)
    cursor = connection.cursor()
    sqlCMD = "SELECT max(pDate) from %s"%(tableName)
    cursor.execute(sqlCMD)
    results = cursor.fetchall()
    if len(results) == 1 and results[0][0] != None:
        startDate= results[0][0]
    
    emails = [email for email in EMailDownloader.getEmails(since=startDate)]
    if len(emails) == 0: return 0
    
    cPickle.dump(emails, open(N.MAILARCHIVES +  "MailArchive%s.pkl"%(datetime.datetime.now()), 'wb'))
    
    jobs = []
    for email in emails:
        jobs.extend(email.parse())
    EMailSqlDump.dumpJobOffersToSQL(jobs)
    
    return len(emails)
    
if __name__ == '__main__':
    downloadAvailableEMails()

