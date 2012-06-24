import re
import cPickle
import EMailDownloader
import os
import datetime
import JobDescriptor
import EMailSqlDump

class EMail:
    def __init__(self, sender, receiver, subject, body, dateReceivedStr):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.body = body
        self.jobHeader = None
        self.dateReceivedStr = dateReceivedStr.split('Date: ')[-1]
    def jobOffers(self):
        msgContents = self.body.split('\n')
        startLine = 0
        numJobTitlesFound = 0
        self.jobHeader = []
        for i in xrange(startLine, len(msgContents)):
            line = msgContents[i]
            startLine = i
            if line[:len('Job Title:')] == 'Job Title:':
                #We need to iterate down to the first job posting (represented by Job Title: information), but there is a summary of the search first, so skip first mention of job title
                numJobTitlesFound += 1
                if numJobTitlesFound>1: break
            self.jobHeader.append(line)

        if startLine > 0.5*len(msgContents):
            raise Exception("Probably misparsed the starting location for job offers in the email message:"+self.body)
        #startingLine should now be the line number of the start of the first job offer
        for i in xrange(startLine+1, len(msgContents)):
            line = msgContents[i]
            if line[:len('Job Title:')] == 'Job Title:':
                #We've hit the next Job offer, so return the current job offer, and be ready for the next one
                yield msgContents[startLine:i-1]
                startLine = i
        yield msgContents[startLine:]

    def convertToDict(self, jobOffer):
        toReturn = {}
        parts = set(['Job Title', 'Location', 'Salary', 'Start Date', 'Duration', 'Description', 'http'])
        toAdd = []
        previousHeader = None
        for line in jobOffer:
            tokens = line.split(':')
            header = tokens[0]
            if line[:len('____________________')] == '____________________': break
            if header in parts:
                if previousHeader != None:
                    toReturn[previousHeader] = ''.join(toAdd)
                previousHeader = header
                toAdd = [':'.join(tokens[1:])]
                
            else: toAdd.append(line)
        if toAdd[0][:2] != '//':
            raise Exception("Did not parse the URL correctly!")
        toReturn['URL'] = 'http:'+toAdd[0]
        return toReturn
        
    def parse(self):
        jobs = []
        if '<HTML>' in self.body: 
            #return self.parseHTML() #For now, just ignore HTML emails
            return []
        for jobOffer in self.jobOffers():
            jobOfferParts = self.convertToDict(jobOffer)
            job = JobDescriptor.JobDescriptor()
            job.pDate = self.dateReceivedStr
            job.jobTitle = jobOfferParts['Job Title'].strip(' ')
            job.salaryString = jobOfferParts['Salary'].strip(' ')
            job.startDate = jobOfferParts['Start Date'].strip(' ')
            job.duration = jobOfferParts['Duration'].strip(' ')
            job.city = jobOfferParts['Location'].strip(' ')
            job.longDescription = jobOfferParts['Description'].strip(' ')
            job.URL = jobOfferParts['URL'].strip(' ')

            job.fillInMissingEntries('\n'.join(self.jobHeader))
            
            #if job.salary_lower == None:
            #    print "Error!"
            #    print '\n'.join(jobOffer)
            #    print "*"*20
            jobs.append(job)
        return jobs

if __name__ == '__main__':
    emails = []
    
    if not os.path.exists("MailArchive2012-06-08 17-49-05.296393.pkl"):
        for email in EMailDownloader.getEmails(since=datetime.datetime(2012,6,7,23,24,34)):
            emails.append(email)
        print len(emails)
        cPickle.dump(emails, open("MailArchive2012-06-08 17-49-05.296393.pkl"))

    emails = cPickle.load(open("MailArchive2012-06-08 17-49-05.296393.pkl","rb"))
    jobs = []
    for email in emails:
        jobsToAdd = email.parse()
        if len(jobsToAdd) == 0:
            print email.dateReceivedStr
        jobs.extend(email.parse())
    #for job in jobs:
    #    print job.pDate
    EMailSqlDump.dumpJobOffersToSQL(jobs)
