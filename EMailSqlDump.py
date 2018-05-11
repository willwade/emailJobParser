import MySQLdb
import datetime, time
import NHS_JOBS_CONSTANTS as N

def getPostedJobsAndCounts(cursor, tableName, jobs):
    sqlCMD = "SELECT uniqurlid, repostedcnt from %s WHERE uniqurlid in (%s)" \
            %(tableName, ",".join(map(lambda j:str(int(j.uniqueURLID)), jobs)))
    cursor.execute(sqlCMD)
    results = cursor.fetchall()
    toReturn = {}
    for uniqueURL, count in results:
        toReturn[str(uniqueURL)] = count
    return toReturn
    
def updateRepostedCount(cursor, tableName, url, count):
    sqlCMD = "UPDATE %s SET repostedcnt=%i where uniqurlid='%i'" %(tableName, count, url)
    cursor.execute('BEGIN')
    cursor.execute(sqlCMD)
    cursor.execute('COMMIT')
    
''' REMOVE LATER

def getPostedJobsAndCounts(cursor, tableName):
    sqlCMD = "SELECT uniqurlid, repostedcnt from %s " %(tableName)
    cursor.execute(sqlCMD)
    results = cursor.fetchall()
    toReturn = {}
    for uniqueURL, count in results:
        toReturn[uniqueURL] = count
    return toReturn

def dumpJobOffersToSQL(jobOffers, timestamp=time.time()):
    connection = MySQLdb.connect(N.SQL_HOST_NAME, N.SQL_USER_NAME, N.SQL_PASSWD, N.SQL_DB)
    cursor = connection.cursor()
    
    alreadyPostedJobs = getPostedJobsAndCounts(cursor, N.JOBS_DETAIL_TABLENAME)
    
    for jobOffer in jobOffers:
        if int(jobOffer.uniqueURLID) in alreadyPostedJobs: 
            alreadyPostedJobs[int(jobOffer.uniqueURLID)]+=1
            updateRepostedCount(cursor, N.JOBS_DETAIL_TABLENAME, int(jobOffer.uniqueURLID), alreadyPostedJobs[int(jobOffer.uniqueURLID)])
        else:
            dumpJobOffer(jobOffer, tableName = N.JOBS_DETAIL_TABLENAME, cursor = cursor, timestamp = timestamp)
    
    dumpJobOfferSummary(jobOffers, timestamp, tableName = N.JOBS_SUMMARY_TABLENAME, cursor=cursor)
    dumpBand5OfferSummary(jobOffers, timestamp, tableName = N.JOBS_BAND5_SUMMARY_TABLENAME, cursor=cursor)
'''

def dumpJobOffer(o, tableName, cursor, timestamp):
    sqlCMD = 'INSERT INTO %s (tstamp, pDate, uname, title, band, location, salary, salary_lower, salary_higher, pro_rata, stDate, duration, descr, lat, lon, city, status, url, repostedcnt, uniqurlid, fixedband, source) VALUES\
                                  (%i, "%s",  "%s", "%s",  "%s",   "%s",     "%s",       %s,          %s,          %s,     "%s",    "%s",    "%s", "%s","%s","%s",  "%s",  "%s",      %s,        %s,      %s,"%s") \
             '%(tableName, timestamp,o.pDate,o.uniqueURLID, o.jobTitle, o.band, o.city, o.salaryString, o.salary_lower, o.salary_higher, o.proRata, o.startDate, o.duration, o.longDescription.replace('"',"'"), o.latitude, o.longitude, o.city, o.status, o.URL, 1, o.uniqueURLID, o.fixedBand, o.source)
    sqlCMD = sqlCMD.replace("'None'","NULL").replace("None","NULL")
    cursor.execute('BEGIN')
    cursor.execute(sqlCMD)
    cursor.execute('COMMIT')

def dumpJobOfferSummary(jobOffers, timestamp, tableName, cursor):

    postedDateToJobOffers = {}
    for jobOffer in jobOffers:
        pDate = jobOffer.pDate
        simpleDate = datetime.date(pDate.year, pDate.month, pDate.day)
        if simpleDate not in postedDateToJobOffers: postedDateToJobOffers[simpleDate] = []
        postedDateToJobOffers[simpleDate].append(jobOffer)
    
    bands = set(["0",'1','2','3','4','5','6','7','8a','8b','8c','8d','9'])

    postedDates = postedDateToJobOffers.keys()
    postedDates.sort()
    for pDate in postedDates:
        jobOffers = postedDateToJobOffers[pDate]
        
        bandToNumbers = {}
        numJobs = 0
        numTemp = 0
        numPerm = 0

        for jobOffer in jobOffers:
            if jobOffer.band != None:
                for bandNum in jobOffer.band:
                    if bandNum in bands:
                        bandToNumbers[bandNum] = bandToNumbers.get(bandNum, 0)+1
            numJobs += 1
            if jobOffer.duration == 'Permanent': numPerm += 1
            elif jobOffer.duration == 'Part Time': numTemp += 1
        
        #Now see if this pDate is already in the summary db!
        sqlCMD = "SELECT id, tstamp, number, numberTemp, numberPerm, numberbandf, numberbands, numberbandse, numberbande from %s where pDate = '%s'" %(tableName, pDate)
        cursor.execute(sqlCMD)
        results = cursor.fetchall()
        if len(results) == 1:
            id, ptstamp, pNum, pNumTemp, pNumPerm, pNumBandF, pNumBandS, pNumBandSe, pNumBandE = results[0]
            sqlCMD = "UPDATE %s SET tstamp = %i, number=%i, numberTemp=%i, numberPerm=%i, numberbandf=%i, numberbands=%u, numberbandse=%i, numberbande=%i where id=%i"%(tableName, timestamp, numJobs+pNum, numTemp+pNumTemp, numPerm+pNumPerm, bandToNumbers.get('5',0) + pNumBandF, bandToNumbers.get('6',0) + pNumBandS, bandToNumbers.get('7',0) + pNumBandSe, sum( (bandToNumbers.get('8a',0),bandToNumbers.get('8b',0),bandToNumbers.get('8c',0),bandToNumbers.get('8d',0),bandToNumbers.get('8',0)) ) + pNumBandE, id)
            cursor.execute('BEGIN')
            cursor.execute(sqlCMD)
            cursor.execute('COMMIT')
        else:
            sqlCMD = "INSERT INTO %s (tstamp, number, numberTemp, numberPerm, numberbandf, numberbands, numberbandse, numberbande, pdate) VALUES (%i, %i, %i, %i, %i, %i, %i, %i, '%s')" % (tableName, timestamp, numJobs, numTemp, numPerm, bandToNumbers.get('5',0), bandToNumbers.get('6',0), bandToNumbers.get('7',0), sum( (bandToNumbers.get('8a',0),bandToNumbers.get('8b',0),bandToNumbers.get('8c',0),bandToNumbers.get('8d',0),bandToNumbers.get('8',0))), pDate )
            cursor.execute('BEGIN')
            cursor.execute(sqlCMD)
            cursor.execute('COMMIT')

def dumpBand5OfferSummary(jobOffers, timestamp, tableName, cursor):
    postedDateToJobOffers = {}
    for jobOffer in jobOffers:
        pDate = jobOffer.pDate
        simpleDate = datetime.date(pDate.year, pDate.month, pDate.day)
        if simpleDate not in postedDateToJobOffers: postedDateToJobOffers[simpleDate] = []
        postedDateToJobOffers[simpleDate].append(jobOffer)

    postedDates = postedDateToJobOffers.keys()
    postedDates.sort()
    for pDate in postedDates:
        jobOffers = postedDateToJobOffers[pDate]
        number = 0
        for jobOffer in jobOffers:
            if jobOffer.band != None and '5' in jobOffer.band:
                number += 1
        #Now see if this postedDate is already in the summary db!
        sqlCMD = "SELECT id, pdate, number from %s where pDate = '%s'" %(tableName, pDate)
        cursor.execute(sqlCMD)
        results = cursor.fetchall()
        if len(results) == 1:
            id, foo, pNumber = results[0]
            sqlCMD = "UPDATE %s SET number=%i where id=%i" %(tableName, number+pNumber, id)
            cursor.execute('BEGIN')
            cursor.execute(sqlCMD)
            cursor.execute('COMMIT')
        else:
            sqlCMD = "INSERT INTO %s (pdate, number) VALUES ('%s', %i)"%(tableName, pDate, number)
            cursor.execute('BEGIN')
            cursor.execute(sqlCMD)
            cursor.execute('COMMIT')
