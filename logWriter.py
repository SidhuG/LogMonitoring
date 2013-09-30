from logging.handlers import SysLogHandler
from logging import Logger, Formatter
import random
import sys
import os
import time
from decimal import Decimal

logLevels = [SysLogHandler.LOG_EMERG, \
            SysLogHandler.LOG_ALERT, \
            SysLogHandler.LOG_CRIT, \
            SysLogHandler.LOG_ERR, \
            SysLogHandler.LOG_WARNING, \
            SysLogHandler.LOG_NOTICE, \
            SysLogHandler.LOG_INFO, \
            SysLogHandler.LOG_DEBUG]

logLevelStr = { SysLogHandler.LOG_EMERG: " EMER      ",\
                SysLogHandler.LOG_ALERT: " ALERT     ",\
                SysLogHandler.LOG_CRIT: " CRITICAL  ",\
                SysLogHandler.LOG_ERR:  " ERROR     ",\
                SysLogHandler.LOG_WARNING: " WARN      ",\
                SysLogHandler.LOG_NOTICE: " NOTE      ",\
                SysLogHandler.LOG_INFO: " INFO      ",\
                SysLogHandler.LOG_DEBUG: " DEBUG     "}
                
class logWriter(object):
    def __init__(self, logFacility = SysLogHandler.LOG_LOCAL0):
        format = Formatter("%(levelname)-12s %(asctime)s %(process)d %(message)s")
                 
        self.sLogger = Logger(SysLogHandler.LOG_DEBUG)
        #self.sLogger.setLevel()

        self.sysHandler = SysLogHandler(address = '/dev/log', facility = logFacility)
        self.sysHandler.setFormatter(format)
        self.sLogger.addHandler(self.sysHandler)
    
    def __del__(self):
        self.sysHandler.flush()
        self.sysHandler.close()
        
    def sendMsg(self, level, msg):
        self.sLogger.log(level,logLevelStr[level] + msg)
        
if __name__ == "__main__":
    logwriterObj0 = logWriter(SysLogHandler.LOG_LOCAL0)
    logwriterObj1 = logWriter(SysLogHandler.LOG_LOCAL1)
    logwriterObj2 = logWriter(SysLogHandler.LOG_LOCAL2)
    logwriterObj3 = logWriter(SysLogHandler.LOG_LOCAL3)
    
    logWriterTup = (logwriterObj0,logwriterObj1, logwriterObj2,logwriterObj3)
    
    while 1:
        logLevel = random.choice(logLevels)
        logWriterObj = random.choice(logWriterTup)
        logWriterObj.sendMsg(logLevel, "logWriterObj Msg")
    
        randDelay = random.randint(10,300)
        randDelayms = Decimal(randDelay)/100
        
        time.sleep(randDelayms)
