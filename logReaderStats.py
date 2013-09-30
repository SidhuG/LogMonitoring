from optparse import OptionParser
from logging.handlers import SysLogHandler
import fileinput
import re
import datetime
import sys

logLevelStr = { "EMER",\
                "ALERT",\
                "CRITICAL",\
                "ERROR",\
                "WARN",\
                "NOTE",\
                "INFO",\
                "DEBUG"}

class logLevelStats(object):
    def __init__(self, level, logDuration=1):
        if level not in range(len(logLevelStr)):
            self.level = -1
            self.basetime = 0
            self.logduration =0
        else:
            self.level = level
            self.logduration = logDuration
            self.basetime = datetime.datetime.now() - datetime.timedelta(hours=logDuration)
        self.listtime = []
    
    def setLogEntry(self, pid, time):
        if self.level != -1:
            logTime = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            if ( logTime > self.basetime):
                listEntry= {"PID":pid, "logtime":logtime}
                self.listtime.append(listEntry)
                #print "log time added"
                #print "basetime"
                #print self.basetime
                #print " "
            nowtime  = datetime.datetime.now()
            #print "nowtime"
            #print nowtime
            #print " "
            
            if ( (nowtime - self.basetime) > datetime.timedelta(hours=self.logduration)):
                self.basetime = nowtime - datetime.timedelta(hours=self.logduration)
                #print "new basetime"
                #print self.basetime
                #print " "
                #delete records older than logDuration hours
                for entryinlist in self.listtime:
                    #print entryinlist["logtime"]
                    if ( datetime.datetime.strptime(entryinlist["logtime"], "%Y-%m-%d %H:%M:%S") < self.basetime):
                        self.listtime.remove(entryinlist)
                        #print entryinlist["logtime"]
                        #print "Log time deleted"
                        #print " "
                    else:
                        break
    
    def getLogDetails(self):
        return self.listtime
    
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print "Usage"
        print "logReaderStats.py -f <filename> -t <hours>"
        raise SystemExit(1)
    
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
        help="Open file for reading", metavar="FILE")
    
    parser.add_option("-t", "--hours",
                  dest="T", default=1,type="int",
                  help="No of hours to be used for analysis")
    
    (options, args) = parser.parse_args()
    filename = options.filename
    hours = options.T
    print 'To analyse ' + str(options.T) + ' hours of log from file ' + str(options.filename)
    
    statDebug = logLevelStats(level=7, logDuration = hours)
    statInfo = logLevelStats(level=6, logDuration = hours)
    statNote = logLevelStats(level=5, logDuration = hours)
    statWarn = logLevelStats(level=4, logDuration = hours)
    statErr = logLevelStats(level=3, logDuration = hours)
    statCrit = logLevelStats(level=2, logDuration = hours)
    statAlert = logLevelStats(level=1, logDuration = hours)
    statEmer = logLevelStats(level=0, logDuration = hours)
    
    datePattern = '2013-09-27 17:00:01'
   
    #extfile = open(filename, 'r')
    #fileinputObj = fileinput.FileInput(filename)
    returnList = []
    lineno = 0
    lastReadPos = 0
    fileinputObj = None
    while 1:
        try:
            if fileinputObj is None:
                #fileinputObj = fileinput.input(filename)
                fileinputObj = open(filename, 'r')
            #line = fileinputObj.next()
            fileinputObj.seek(lastReadPos,0)
            line = fileinputObj.readline()
            lineno += 1# fileinputObj.filelineno()
            lastReadPos = fileinputObj.tell()
        except IOError:
            print 'Cannot open file %s for reading' % filename
            import sys
            sys.exit(0)
        if line:
            for pattern in logLevelStr:
                match = re.search(pattern,  line)
                if match:
                    time_re = re.compile('\d{4}[-/]\d{2}[-/]\d{2}')
                    timematch = re.search(time_re, line)
                    s = timematch.start()
                    e = s+len(datePattern)
                    logtime = line[s:e]
                    logpid  = line[e:].split(' ') 
                    #print "logtime"
                    #print logtime
                    #print "logpid"
                    #print logpid[1]
                    if pattern == "DEBUG": #logLevelStr[SysLogHandler.LOG_DEBUG]:
                        #print "DEBUG"
                        statDebug.setLogEntry(logpid[1], logtime)
                        result = {"ERRTYPE":"DEBUG","STATS": statDebug.getLogDetails()}
                    elif pattern == "INFO":
                        #print "INFO"
                        statInfo.setLogEntry(logpid[1], logtime)
                        result = {"ERRTYPE":"INFO","STATS": statInfo.getLogDetails()}
                    elif pattern == "NOTE":
                        #print "NOTE"
                        statNote.setLogEntry(logpid[1], logtime)
                        result = {"ERRTYPE": "NOTE","STATS": statNote.getLogDetails()}
                    elif pattern == "WARN":
                        #print "WARN"
                        statWarn.setLogEntry(logpid[1], logtime)
                        result = {"ERRTYPE": "WARN","STATS": statWarn.getLogDetails()}
                    elif pattern == "ERROR":
                        #print "ERROR"
                        statErr.setLogEntry(logpid[1], logtime)
                        result = {"ERRTYPE": "ERROR","STATS": statErr.getLogDetails()}
                    elif pattern == "CRITICAL":
                        #print "CRITICAL"
                        statCrit.setLogEntry(logpid[1], logtime)
                        result = {"ERRTYPE": "CRITICAL","STATS": statCrit.getLogDetails()}
                    elif pattern == "ALERT":
                        #print "ALERT"
                        statAlert.setLogEntry(logpid[1], logtime)
                        result = {"ERRTYPE": "ALERT","STATS": statAlert.getLogDetails()}
                    elif pattern == "EMER":
                        #print "EMER"
                        statEmer.setLogEntry(logpid[1], logtime)
                        result = {"ERRTYPE": "EMER","STATS": statEmer.getLogDetails()}
                    print result
        else:
            fileinputObj.close()
            del fileinputObj
            fileinputObj = None
            

