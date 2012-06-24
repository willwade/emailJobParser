import datetime
import smtplib
import email
import socket
import MakeCharts

import NHS_JOBS_CONSTANTS as N

def sendEmailUpdate():
	filesToAttach = MakeCharts.createSummaryCharts()
	subject = "Jobs Summary Report for %s"%(datetime.date.today())
	text = "Attached, please find the summary report as of %s"%(datetime.date.today())
	sendMail(None, "willwade@gmail.com", subject, text, files=filesToAttach)
	
def sendMail(fro, to, subject, text, files=[], numSendTries=2, timeoutSecsPerTry=20):
	"""This function sends a email with text and attachements if provided.
	"""
		
	
	if isinstance(to, str):
		to = [to]
	assert type(files) == list
	
	if fro == None:
		fro = N.ACCOUNT_NAME
	
	msg = email.MIMEMultipart.MIMEMultipart()
	msg['From'] = fro
	msg['To'] = email.Utils.COMMASPACE.join(to)
	msg['Date'] = email.Utils.formatdate(localtime = True)
	msg['Subject'] = subject
	msg.attach(email.MIMEText.MIMEText(text))
	
	for alink, afile, fileName in files:
            msg.attach(email.MIMEText.MIMEText("This is the link for this chart %s" %(alink)))
            part = email.MIMEBase.MIMEBase("application", "octet-stream")
            part.set_payload(afile.read())
            email.Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachement; filename="%s"' % fileName)
            msg.attach(part)
	
	#smtplib.SMTP.set_debuglevel(True) #debugging code
	done = False
	tries = 0
	
	while not done:
		if tries > numSendTries: return
		oldTimeout = socket.getdefaulttimeout()
		socket.setdefaulttimeout(timeoutSecsPerTry)
		server = smtplib.SMTP(N.SMTP_SERVER)
		socket.setdefaulttimeout(oldTimeout)

		server.ehlo()
		server.starttls()
		server.ehlo()

		try:
			server.login(N.ACCOUNT_NAME, N.ACCOUNT_PASSWD)
		except smtplib.SMTPException, e:
			print "This could be a problem with your anti-virus.\nPlease try disabling it and trying again.\n"
			raise e

		try:
			err = server.sendmail(fro, to, msg.as_string())
			done = True
		except Exception, e:
			if tries >= numSendTries: raise e

		server.close()	
		tries += 1

if __name__ == '__main__': 
	sendEmailUpdate()
