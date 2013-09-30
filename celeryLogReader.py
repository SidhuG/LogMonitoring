#from logging.handlers import SysLogHandler
#import fileinput
import re
import datetime
import sys
from flask import jsonify
from celery import Celery
celery = Celery('celeryLogReader', backend='amqp',broker='amqp://guest@localhost//')    
from threading import Lock

mutex = Lock()

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
			print logTime
			if ( logTime > self.basetime):
				listEntry= {"PID":pid, "logtime":time}
				self.listtime.append(listEntry)
				print listEntry
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
					#if ( entryinlist["logtime"] < self.basetime):
						self.listtime.remove(entryinlist)
						#print entryinlist["logtime"]
						#print "Log time deleted"
						#print " "
					else:
						break
	
	def getLogDetails(self):
		return self.listtime

@celery.task
def logReaderTask(file=None, hours=None):
	
	filename = "/var/log/" + file
	print 'To analyse ' + filename + ' hours of log from file '
	
	statDebug = logLevelStats(level=7, logDuration = hours)
	statInfo = logLevelStats(level=6, logDuration = hours)
	statNote = logLevelStats(level=5, logDuration = hours)
	statWarn = logLevelStats(level=4, logDuration = hours)
	statErr = logLevelStats(level=3, logDuration = hours)
	statCrit = logLevelStats(level=2, logDuration = hours)
	statAlert = logLevelStats(level=1, logDuration = hours)
	statEmer = logLevelStats(level=0, logDuration = hours)
	
	datePattern = '2013-09-27 17:00:01'

	returnList = []
	lineno = 0
	lastReadPos = 0
	fileinputObj = None
	while(1):
		try:
			if fileinputObj is None:
				fileinputObj = open(filename, 'r')
			fileinputObj.seek(lastReadPos,0)
			line = fileinputObj.readline()
			lineno += 1# fileinputObj.filelineno()
			lastReadPos = fileinputObj.tell()
		except IOError:
			print 'Cannot open file %s for reading' % filename
			return returnList
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
					#print "logpid"
					#print logpid
					#print logtime
					if pattern == "DEBUG":
						statDebug.setLogEntry(logpid[1], logtime)
					elif pattern == "INFO":
						statInfo.setLogEntry(logpid[1], logtime)
					elif pattern == "NOTE":
						statNote.setLogEntry(logpid[1], logtime)
					elif pattern == "WARN":
						statWarn.setLogEntry(logpid[1], logtime)
					elif pattern == "ERROR":
						statErr.setLogEntry(logpid[1], logtime)
					elif pattern == "CRITICAL":
						statCrit.setLogEntry(logpid[1], logtime)
					elif pattern == "ALERT":
						statAlert.setLogEntry(logpid[1], logtime)
					elif pattern == "EMER":
						statEmer.setLogEntry(logpid[1], logtime)
		else:
			fileinputObj.close()
			del fileinputObj
			fileinputObj = None
			break
	debugResult = {"ERRTYPE":"DEBUG","STATS": statDebug.getLogDetails()}
	returnList.append(debugResult)
	infoResult = {"ERRTYPE": "INFO","STATS": statInfo.getLogDetails()}
	returnList.append(infoResult)
	noteResult = {"ERRTYPE": "NOTE","STATS": statNote.getLogDetails()}
	returnList.append(noteResult)
	warnResult = {"ERRTYPE": "WARN","STATS": statWarn.getLogDetails()}
	returnList.append(warnResult)
	errorResult = {"ERRTYPE": "ERROR","STATS": statErr.getLogDetails()}
	returnList.append(errorResult)
	critResult = {"ERRTYPE": "CRITICAL","STATS": statCrit.getLogDetails()}
	returnList.append(critResult)
	alertResult = {"ERRTYPE": "ALERT","STATS": statAlert.getLogDetails()}
	returnList.append(alertResult)
	emerResult = {"ERRTYPE": "EMER","STATS": statEmer.getLogDetails()}
	returnList.append(emerResult)
	return returnList
	
