from schedule import Job
import EMailSqlDump
import EMailDownloader
import MySQLdb
import EMailUpdates
import NHS_JOBS_CONSTANTS as N
import sys
import logging
from JobDescriptor import JobDescriptor

class UpdateJob(Job):
    '''
      Input timestamp is start time of the job. And it's a unique number 
        for each UpdateJob. 
      It will be used to fetch jobs related to this UpdateJob
    '''
    def __init__(self, timestamp, startDate, process_step_count,
                 interval, scheduler=None):
        super(UpdateJob, self).__init__(interval, scheduler)
        self.startDate = startDate
        self.timestamp = int(timestamp)
        self.process_step_count = process_step_count
        self.getEmailsGenerator = EMailDownloader.getEmails(since=startDate)
        self.db = None
        self.processed_count = 0

    def process(self):
        self.db = MySQLdb.connect(host=N.SQL_HOST_NAME,user=N.SQL_USER_NAME,passwd=N.SQL_PASSWD,db=N.SQL_DB)
        cursor = self.db.cursor()
        didfinish = False
        self.db.autocommit(False)
        try:
            for i in range(self.process_step_count):
                try:
                    if self.processed_count >= N.UPDATE_JOB_MAX_PROCESSED:
                        didfinish = True
                        break
                    if self.process_email(next(self.getEmailsGenerator), cursor):
                        self.processed_count += 1
                except StopIteration:
                    didfinish = True
                    break
            logging.info("Processed email: " + str(self.processed_count))
            if didfinish:
                self.scheduler.cancel_job(self)
                if self.processed_count > 0:
                    self.finish(cursor)
            self.db.commit()
        except:
            self.db.rollback()
            self.scheduler.cancel_job(self)
            logging.exception("Failed at processing email")
        cursor.close()
        self.db.close()
    
    def process_email(self, email, cursor):
        jobOffers = email.parse()
        if len(jobOffers) == 0:
            logging.debug("Could not find jobOffers for email at: " + str(email.dateReceivedStr).strip() + ", subject: " + str(email.subject).strip());
            return False
        alreadyPostedJobs = EMailSqlDump.getPostedJobsAndCounts(cursor, N.JOBS_DETAIL_TABLENAME, jobOffers)
        for jobOffer in jobOffers:
            if str(jobOffer.uniqueURLID) in alreadyPostedJobs: 
                alreadyPostedJobs[str(jobOffer.uniqueURLID)]+=1
                EMailSqlDump.updateRepostedCount(cursor, N.JOBS_DETAIL_TABLENAME, int(jobOffer.uniqueURLID), alreadyPostedJobs[str(jobOffer.uniqueURLID)])
            else:
                EMailSqlDump.dumpJobOffer(jobOffer, tableName = N.JOBS_DETAIL_TABLENAME, cursor = cursor, timestamp = self.timestamp)
        return True
    
    def finish(self, cursor):
        try:
            jobOffers = list(self.fetchJobOffers())
            if len(jobOffers) == 0:
                raise Exception("!No job offers!")
            EMailSqlDump.dumpJobOfferSummary(jobOffers, self.timestamp, tableName = N.JOBS_SUMMARY_TABLENAME, cursor=cursor)
            EMailSqlDump.dumpBand5OfferSummary(jobOffers, self.timestamp, tableName = N.JOBS_BAND5_SUMMARY_TABLENAME, cursor=cursor)
            EMailUpdates.sendEmailUpdate()
            logging.info("Finish, processed count: " + str(self.processed_count))
            return True
        except:
            logging.exception("Failed to finish UpdateJob")
            return False
      
    def fetchJobOffers(self):
        cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
        sqlCMD = "SELECT * from %s WHERE `tstamp`=%s" % \
                 ('otjobs', str(self.timestamp))
        cursor.execute(sqlCMD)
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            o = JobDescriptor()
            o.timestamp = row['tstamp']
            o.pDate = row['pDate']
            o.uniqueURLID = row['uniqurlid']
            o.jobTitle = row['title']
            o.band = row['band']
            o.location = row['city']
            o.salaryString = row['salary']
            o.salary_lower = row['salary_lower']
            o.salary_higher = row['salary_higher']
            o.proRata = row['pro_rata']
            o.startDate = row['stDate']
            o.duration = row['duration']
            o.longDescription = row['descr']
            o.latitude = row['lat']
            o.longitude = row['lon']
            o.city = row['city']
            o.status = row['status']
            o.URL = row['url']
            o.fixedBand = row['fixedband']
            o.source = row['source']
            yield o


