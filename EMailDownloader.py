#Fri Jul 23 12:51:57 IST 2010
# pygmail.py - A Python Library For Gmail
# http://segfault.in/2010/07/playing-with-python-and-gmail-part-1/
    
import pygmail
import EMail
import datetime
import dateutil.parser
import NHS_JOBS_CONSTANTS as N

def getEmails(since=None, accountName=N.ACCOUNT_NAME, accountPasswd=N.ACCOUNT_PASSWD, emailFolder=N.FOLDER, sender=N.SENDER):
    g = pygmail.pygmail()
    g.login(accountName, accountPasswd)
    ids = g.get_mails_from(sender,emailFolder, since=since)
    if since != None and not since.tzinfo:
        since = dateutil.parser.parse(str(since)+' +0000')
    for id in ids:
        status, response = g.get_date_received_from_id(id)
        dateReceivedStr = response[0][1]
        
        dateReceived = dateutil.parser.parse(dateReceivedStr.split('Date:')[1].strip())
        if not dateReceived.tzinfo:
            dateReceived = dateutil.parser.parse(dateReceivedStr.split('Date:')[1].strip() + ' +0000')
        
        if since != None and  dateReceived <= since: continue #We have already downloaded this email!
        status, response = g.get_subject_from_id(id)
        subject = response[0][1]
        status, response = g.get_body_from_id(id)
        body = response[0][1]
        yield EMail.EMail(sender=sender, receiver=accountName, subject=subject, body=cleanupEmailText(body), dateReceivedStr = dateReceivedStr)

        
def cleanupEmailText(txt):
    "Cleans up some of the formatting of email text"
    #Remove annoying carriage returns if they exist
    txt = txt.replace('\r\n','\n').replace('\r','\n')
    #Combine any lines that end with the line continuation character '='
    txt = txt.replace("=\n","")
    #Replace the blank space symbol =20 with nothing
    txt = txt.replace('=20','')
    
    return txt
    
