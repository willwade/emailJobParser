import schedule
import MySQLdb
import time
import datetime
import dateutil
import dateutil.tz
import NHS_JOBS_CONSTANTS as N
from UpdateJob import UpdateJob
from sys import argv, exit
import logging
import os

_dir = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(filename=os.path.join(_dir,'exe-' +  datetime.datetime.now().strftime('%Y-%m-%d') + '.log'),
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.DEBUG)
time.tzset()

external_vars = ['ACCOUNT_NAME', 'ACCOUNT_PASSWD', 'SQL_USER_NAME', 'SQL_PASSWD', 'SQL_DB', 'SENDER']
for external_var in external_vars:
    if external_var in os.environ and os.environ[external_var] != "":
        setattr(N, external_var, os.environ[external_var])

def schedule_update():
        # get fetch startDate
    logging.info('schedule_update start')
    tableName = N.JOBS_DETAIL_TABLENAME
    startDate = datetime.datetime(2000,1,1, tzinfo = dateutil.tz.tzoffset(None,0))
    connection = MySQLdb.connect(host=N.SQL_HOST_NAME,user=N.SQL_USER_NAME,passwd=N.SQL_PASSWD,db=N.SQL_DB)
    cursor = connection.cursor()
    sqlCMD = "SELECT max(pDate) from %s"%(tableName)
    cursor.execute(sqlCMD)
    results = cursor.fetchall()
    if len(results) == 1 and results[0][0] != None:
        startDate= results[0][0]
    job = UpdateJob(time.time(), startDate, N.UPDATE_JOBS_PROCESS_STEP_COUNT,
                    0.200, schedule.default_scheduler)
    job.unit = 'seconds' # runs every 200 mili-second
    job.do(job.process)

def run():
    N.UPDATE_JOBS_INTERVAL.do(schedule_update)
    while True:
        schedule.run_pending()
        if schedule.next_run() is None:
            break
        time.sleep(schedule.idle_seconds())

if __name__ == '__main__':
    logging.info("Daemon Started")
    if len(argv) > 1:
        if argv[1] == 'oncenow':
            schedule_update()
            while True:
                schedule.run_pending()
                if schedule.next_run() is None:
                    break
                time.sleep(schedule.idle_seconds())
            exit(0)
    run()
    logging.info("Daemon Exit")
