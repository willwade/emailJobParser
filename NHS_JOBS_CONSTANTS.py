
SENDER = 'nhs-vac@nhscareersjobs.co.uk'
FOLDER = 'OT:Jobs'
ACCOUNT_NAME = 'email@gmail.com'
ACCOUNT_PASSWD = 'PASSWORD'

SMTP_SERVER = 'smtp.gmail.com'
SQL_HOST_NAME = 'localhost'
SQL_USER_NAME = 'user'
SQL_PASSWD = 'password'
SQL_DB = 'otjobs'
JOBS_DETAIL_TABLENAME = "otjobs"
JOBS_SUMMARY_TABLENAME = "otjobssummary"
JOBS_BAND5_SUMMARY_TABLENAME = "band5Summary"

TIME_BETWEEN_DOWNLOADS= 60*60*24 #Wait a day between downloading and dumping new job emails to db
TIME_BETWEEN_EMAIL_UPDATES = 7*60*60*24 #Wait a week between sending out e-mail updates
