import re
import urllib
import datetime
import dateutil
import dateutil.parser

class JobDescriptor:
    bandRange = {}
    bandRange['0'] = (0, 13233)
    bandRange['1'] = (0, 13233)
    bandRange['2'] = (13234, 15190)
    bandRange['3'] = (15191, 17732) 
    bandRange['4'] = (17733, 20710)
    bandRange['5'] = (20711, 24831)
    bandRange['6'] = (24832, 29789)
    bandRange['7'] = (29790, 37996)
    bandRange['8a'] = (37997, 44258)
    bandRange['8b'] = (44259, 53256)
    bandRange['8c'] = (53257, 63833)
    bandRange['8d'] = (63834, 75383)
    bandRange['9'] = (75834, None)
    
    def __init__(self):
        
        self.postedDate = None
        self.uniqueName = None
        self.jobTitle = None
        self.band = None
        self.salaryString = None
        self.salary_lower = None
        self.salary_higher = None
        self.proRata = None
        self.startDate = None
        self.duration = None
        self.longDescription = None
        self.latitude = None
        self.longitude = None
        self.city = None
        self.status = None
        self.URL = None
        self.uniqueURLID = None
        self.fixedBand = False
        self.source = None
        self.pDate = None
        self.salaryPattern = re.compile("[0-9]{1,3}[,\.]? ?[0-9]{3,3}\.?[0-9]{0,2}") #Salaries have to be greater than 10000 pounds a year, hopefully a safe assumption
        self.latLongPattern = re.compile("/([-0-9.]+),([-0-9.]+)/")
        self.bandPattern = re.compile("band *[0-9][a-d]?", re.IGNORECASE)
        self.proRataPattern = re.compile("[^0-9a-zA-Z]pr", re.IGNORECASE)
        self.durationPatternPermanent = re.compile("Permanent", re.IGNORECASE)
        self.durationPatternFixed = re.compile("fixed term|temporary|part ?-?time", re.IGNORECASE)
        self.sourcePatterns = {}
        self.sourcePatterns['paed'] = re.compile('Must include children AND paediatrics AND paediatric', re.IGNORECASE)
        self.sourcePatterns['any'] = re.compile("Salary:([ \t]+)Any upwards", re.IGNORECASE)
        self.sourcePatterns['buck1'] = re.compile('Must be within about 30 miles of HP27', re.IGNORECASE)
        self.sourcePatterns['buck2'] = re.compile("Must be within about 30 miles of HP27 {BUCKINGHAMSHIRE}", re.IGNORECASE)
        self.sourcePatterns['b5'] = re.compile('occupational therapist AND \(basic grade OR band 5\)', re.IGNORECASE)
        self.GEOCODE_URL_BASE = 'http://lamp.tinygeocoder:8080/create-api.php?q='
    
    def getSalaryRange(self):
        salaryStr = self.salaryString.replace('=A3','') #Get rid of what is presumably the pound special char
        if len(salaryStr) == 1 and salaryStr in JobDescriptor.bandRange:
            return JobDescriptor.bandRange[salaryStr]
        salaries = self.salaryPattern.findall(salaryStr)
        if len(salaries) == 1:
            self.fixedBand = True
            return JobDescriptor.bandRange[self.reverseBandLookup(float(salaries[0].replace(',','').replace(' ','')))]
        if len(salaries) != 2:
            bandNums = self.findBands()
            if bandNums != None and len(bandNums) != 0:
                minSalary = min( (JobDescriptor.bandRange[bandNum][0] for bandNum in bandNums if bandNum in JobDescriptor.bandRange) )
                maxSalary = max( (JobDescriptor.bandRange[bandNum][1] for bandNum in bandNums if bandNum in JobDescriptor.bandRange) )
                return minSalary, maxSalary
            return None, None
        else:
            if ',' not in salaries[0] and len(salaries[0]) > 4: salaries[0] = salaries[0].replace('.','')
            if ',' not in salaries[1] and len(salaries[1]) > 4: salaries[1] = salaries[1].replace('.','')
            return [float(salary.replace(',','').replace(' ','')) for salary in salaries]
    
    def reverseBandLookup(self, salary):
        for key, range in JobDescriptor.bandRange.iteritems():
            lowVal, highVal = range
            if (lowVal == None or salary >= lowVal) and (highVal == None or salary <= highVal):
                return key
        return None
    
    def findBands(self):
        #First, look in the salaryStr
        salaryStr = self.salaryString
        bandNums = self.bandPattern.findall(salaryStr)
        if len(bandNums) > 0:
            bandNums = [bandNum[4:].strip() for bandNum in bandNums]
            return bandNums
        #Then, look in the Job Title
        bandNums = self.bandPattern.findall(self.jobTitle)
        if len(bandNums) > 0:
            bandNums = [bandNum[4:].strip() for bandNum in bandNums]
            return bandNums
        #Finally, look in the description
        bandNums = self.bandPattern.findall(self.longDescription)
        if len(bandNums) > 0:
            bandNums = [bandNum[4:].strip() for bandNum in bandNums]
            return bandNums
        #Lastly, do a reverseBandLookup on salaryStr if salary_lower is already set!
        if self.salary_lower != None:
            return [self.reverseBandLookup(self.salary_lower)]
        return None
    
    def getLatAndLong(self):
        if self.city == None:
            return 0, 0
        return 0,0
        #I believe this code works, but could not get geocode db to work on my machine
        url = self.GEOCODE_URL_BASE + self.city + "+England"
        f = urllib.urlopen(url)
        contents = f.read()
        tokens = self.latLongPattern.findall(contents)
        if len(tokens) == 2:
            return float(tokens[0]), float(tokens[1])
        else:
            return None, None
    
    def isProRata(self):
        matches = self.proRataPattern.findall(self.salaryString)
        if len(matches) == 1:
            self.proRata = True
        else: self.proRata = False

    def findDuration(self):
        #First look in jobTitle
        if self.durationPatternPermanent.search(self.jobTitle):
            return "Permanent"
        elif self.durationPatternFixed.search(self.jobTitle):
            return "Part Time"
        return "Unknown"
    
    def getUniqueURLId(self):
        if self.URL == None: return None
        urlID = self.URL.split('/')[-1]
        return urlID
    
    def getSource(self, extraInfo):
        for source, pattern in self.sourcePatterns.iteritems():
            if pattern.search(extraInfo):
                return source
    
    def fillInMissingEntries(self, extraInfo = ""):
        self.salary_lower, self.salary_higher = self.getSalaryRange()
        self.band = self.findBands()
        if self.salary_lower != None and self.salary_lower < 100 and self.fixedBand == False:
            print self.salary_lower
            print self.salaryString
            print self.band
            sys.exit(0)
        if self.band != None: self.band = list(set(self.band))
        if self.band == [None] and self.salary_lower != None:
            print self.band
            print self.salaryString
            sys.exit(0)
        self.proRata = self.isProRata()
        self.duration = self.findDuration()
        self.uniqueURLID = self.getUniqueURLId()
        self.source = self.getSource(extraInfo)
        self.latitude, self.longitude = self.getLatAndLong()
        if self.pDate != None:
            self.pDate = dateutil.parser.parse(self.pDate.strip())