import time
import EMailChecker
import EMailUpdates
import NHS_JOBS_CONSTANTS as N

def run():
    timeLastDownloaded = None
    timeLastEmailUpdate = None
    while True:
        curTime = time.time()
        if timeLastDownloaded == None or curTime - timeLastDownloaded > N.TIME_BETWEEN_DOWNLOADS:  
            print "Downloading EMails"
            EMailChecker.downloadAvailableEMails()
            timeLastDownloaded = curTime
        if timeLastEmailUpdate == None or curTime - timeLastEmailUpdate > N.TIME_BETWEEN_EMAIL_UPDATES:
            EMailUpdates.sendEmailUpdate()
            timeLastEmailUpdate = curTime
        time.sleep(60*60) #Wait an hour between checking whether it's time to update the databases or send an e-mail
    
if __name__ == '__main__':
    run()