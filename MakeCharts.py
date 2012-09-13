import pygooglechart
import cStringIO
import MySQLdb
import NHS_JOBS_CONSTANTS as N
import datetime
from pygooglechart import SimpleLineChart
from pygooglechart import Axis

def createSummaryCharts():
    connection = MySQLdb.connect(host=N.SQL_HOST_NAME, user=N.SQL_USER_NAME, passwd=N.SQL_PASSWD, db=N.SQL_DB)
    cursor = connection.cursor()
    chartsToReturn = [] #Will be a list of file-like objects (so we don't have to write to hard disk) which are png's
    rollAvgLink, rollAvgImg = getRollingAverageGraph(cursor, colName = 'number', title = "Number of Jobs", rollingWindowDays=14)
    chartsToReturn.append( (rollAvgLink, rollAvgImg, "Jobs Summary.png") )
    return chartsToReturn

def getRollingAverageGraph(cursor, colName, rollingWindowDays, title=""):
    sqlCMD = "SELECT pDate, %s from %s" %(colName, N.JOBS_SUMMARY_TABLENAME)
    cursor.execute(sqlCMD)
    results = cursor.fetchall()
    
    beginWindowIndex = 0
    endWindowIndex = 0
    xData = []
    yData = []
    while endWindowIndex < len(results):
        while endWindowIndex < len(results) and (results[endWindowIndex][0] - results[beginWindowIndex][0]).days <= rollingWindowDays:
            endWindowIndex += 1
        yData.append( sum(results[i][1] for i in xrange(beginWindowIndex, endWindowIndex, 1)) / float(endWindowIndex - beginWindowIndex))
        xData.append(results[endWindowIndex-1][0])
        beginWindowIndex = endWindowIndex
    chart = SimpleLineChart(680, 400, y_range = (min(yData)-1, max(yData)+1))
    chart.add_data(yData)
    
    yLabels = range(0, int(max(yData)+1), 5)
    yLabels[0] = ''
    xLabels = [str(xData[-i]) for i in xrange(1, len(xData)-1, int(0.2*len(xData)))]
    xLabels.reverse()
    chart.set_axis_labels(Axis.LEFT, yLabels)
    chart.set_axis_labels(Axis.BOTTOM, xLabels)
    chart.set_title("Rolling %i-Day Average %s" % (rollingWindowDays, title))
    chart.download(N.TEMPIMAGE + 'temp.png')
    f = open(N.TEMPIMAGE + 'temp.png','r')
    toReturn = cStringIO.StringIO(f.read())
    f.close()
    toReturn.seek(0)
    return chart.get_url(), toReturn
    
