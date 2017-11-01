#!/usr/bin/python

import os , sys , re , glob , socket, fnmatch, uuid, ConfigParser, logging
from slacker import Slacker
from redminelib import Redmine

configFile = "/etc/ophois/ophois.ini"
host = (socket.gethostname())
rHost = os.environ['SSH_CONNECTION'].split(" ")[0]
loginUser = (os.getlogin())
requestId = uuid.uuid4()
loggingFile = "/var/log/ophois/ophois-login.log"
cmd = 'ps -aeu |grep -i "/bin/ophrec" |grep -iv "bastion" |grep -i "ticket="'
pamHost = os.environ['PAM_HOST']
pamType = os.environ['PAM_TYPE']
serviceName = os.environ['PAM_SERVICE']
rmIssueSubj = loginUser+ " has started a session on host "+host
rmIssueDesc = loginUser+ " has started a session on host "+host
closeNote = "Attaching Session play and Histroy and Closing Issue ticket"
slackNotFallBack = "SSH logout from "+"`"+host+"`"
slackNotText = "SSH logout to "+"`"+host+"`"

def ConfigLoad(configFile):
    Config = ConfigParser.ConfigParser()
    Config.read(configFile)
    # Ophois Configs
    logDir = Config.get('Ophois', 'logDir')
    loginTicketDir = Config.get('Ophois', 'loginTicketDir')
    logLevel = Config.get('Ophois', 'logLevel')
    # Slack Config
    slackNotify = Config.get('Slack', 'slackNotify')
    colorCode = Config.get('Slack', 'colorCode')
    botUser = Config.get('Slack', 'botUser')
    sourceNet = Config.get('Slack', 'sourceNet')
    slackChannel = Config.get('Slack', 'slackChannel')
    # Redmine Config
    redmineNotify = Config.get('Redmine', 'redmineNotify')
    rmUrl = Config.get('Redmine', 'rmUrl')
    rmKey = Config.get('Redmine', 'rmKey')
    rmProjectId = Config.get('Redmine', 'rmProjectId')
    closeNote = Config.get('Redmine', 'closeNote')
    return logDir, loginTicketDir, logLevel, slackNotify, colorCode, botUser, sourceNet, slackChannel, redmineNotify, rmUrl, rmKey, rmProjectId, closeNote

def updateLoginTicket(rmUrl,rmKey,ticket,rmProjectId,closeNote,playFile):
    redmine = Redmine(rmUrl, key=rmKey)
    redmine.issue.update(ticket,
        project_id=rmProjectId,
        tracker_id=9,
        notes=closeNote,
        private_notes=True,
           status_id=3,
        priority_id=3,
        uploads=[{'path': playFile, 'filename': playFile}]
                       )

def slackNotification(slackChannel,botUser,slackNotFallBack,slackNotText,loginUser,serviceName,rHost,sourceNet,colorCode):
    try:
        token = os.environ['token']
        slack = Slacker(token)

        obj = slack.chat.post_message(
            channel=slackChannel,
            text='',
            username=botUser,
            icon_url='https://i.imgur.com/s6d1CKS.png',
            attachments=[{
        "mrkdwn_in": ["text", "fallback"],
        "fallback": slackNotFallBack,
        "text": slackNotText,
        "fields": [{
                "title": "User",
                "value": loginUser,
                "short": "true"
        }, {
                "title": "Service Name",
                "value": serviceName,
                "short": "true"
        }, {
                "title": "IP Address",
                "value": rHost,
                "short": "true"
        }, {
                "title": "Network",
                "value": sourceNet,
                "short": "true"
        }],
        "color": colorCode
}])
        notifyStatus = obj.successful, obj.__dict__['body']['channel'], obj.__dict__[
            'body']['ts']
        print obj.successful, obj.__dict__['body']['channel'], obj.__dict__[
            'body']['ts']
    except KeyError, ex:
        notifyStatus = 'Environment variable %s not set.' % str(ex)
        print 'Environment variable %s not set.' % str(ex)
    return notifyStatus


def listAvailTicket(cmd):
    psOut = os.popen(cmd).read()
    availTicket = (re.findall('ticket=(\d+)', psOut))
    return availTicket

def listOpenTicket(loginTicketDir):
    openTicket = []
    os.chdir(loginTicketDir)
    for i in glob.glob("*"):
        openTicket.append(i)
    return openTicket

def findPlayFile(loginTicketDir,sessId):
    os.chdir('/var/log/bastion/')
    for i in glob.glob("*" + sessId + "*" + ".oph"):
        playFile = i
        return playFile

def ophoisLogoutLogs(loggingFile,loggingType):
    global logger
    global handler
    global formatter
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(loggingFile)
    handler.setLevel(logging.INFO)
    if loggingType == ("func"):
       formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] ' '[' + str(requestId) + '] '  '[' + str(sessId) + '] '  '[' + str(loginUser) + '] ' '[' + str(rHost) + '] ' '[ophois-function-exec] ' '[%(funcName)s] ' '[%(message)s]')
    else:
      formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] ' '[' + str(requestId) + '] '  '[' + str(sessId) + '] ' '[' + str(
            ticket) + '] ' '[' + str(loginUser) + '] ' '[' + str(rHost) + '] ' '[ophois-logout-event] ' '[%(funcName)s] ' '[%(message)s]')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger, handler, formatter

configList =  ConfigLoad(configFile)

logDir = configList[0]
loginTicketDir = configList[1]
logLevel = configList[2]
slackNotify = configList[3]
colorCode = configList[4]
botUser = configList[5]
sourceNet = configList[6]
slackChannel = configList[7]
redmineNotify = configList[8]
rmUrl = configList[9]
rmKey = configList[10]
rmProjectId = configList[11]
closeNote = configList[12]

if pamHost is not re.compile('ip-172-24-1.*'):
    sourceNet = "NON-DMZ"

if  (sourceNet == "DMZ"):
    colorCode = "#008000"
    botUser = "OPHOIS Logout Alert"


if (pamType == "close_session" and slackNotify == "Yes"):
    slackNotification(slackChannel,botUser,slackNotFallBack,slackNotText,loginUser,serviceName,rHost,sourceNet,colorCode)
else:
    print "Slack Notification disabled"

diffTicket = " "
availTicket = listAvailTicket(cmd)
openTicket = listOpenTicket(loginTicketDir)
while diffTicket is not None:
    diffTicket = (set(openTicket) - set(availTicket))
    ticket = (str(diffTicket).split("[")[1].split("]")[0].split("'")[1])
    ticketFile = open("/var/log/ticket/"+str(ticket), "r")
    sessId = ticketFile.read().strip()
    ticketFile.close()
    playFile = findPlayFile("/var/log/basion/", sessId)
    playFilePath = "/var/log/bastion/"+str(playFile)
    loggingType = "logout"
    ophoisLogoutLogs(loggingFile, loggingType)
    logger.info('OPHOIS SSH logout')
    if (redmineNotify == "Yes"):
        updateLoginTicket(rmUrl, rmKey, ticket, rmProjectId, closeNote, playFilePath)
    else:
        print "Login Tracker Disabled"
    os.remove(logDir+playFile)
    break