#!/usr/bin/python

import os , re , uuid , socket , datetime , sys , ConfigParser , logging
from slacker import Slacker
from redminelib import Redmine

configFile = "/etc/ophois/ophois.ini"
rHost = os.environ['SSH_CONNECTION'].split(" ")[0]
sessId = uuid.uuid4().hex
requestId = uuid.uuid4()
date = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
host = (socket.gethostname())
loginUser = (os.getlogin())
logFile = date +"_"+loginUser
loggingFile = "/var/log/ophois/ophois-login.log"
rmIssueSubj = loginUser+ " has started a session on host "+host
rmIssueDesc = loginUser+ " has started a session on host "+host
slackNotFallBack = "SSH login to "+"`"+host+"`"
slackNotText = "SSH login to "+"`"+host+"`"
slackNotFallBackCmd = loginUser+ " tried to establish non-interactive SSH session"
slackNotTextCmd = loginUser+ " tried to establish non-interactive SSH session"

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


def createLoginTicket(rmUrl,rmKey,rmProjectId,rmIssueSubj,rmIssueDesc,sessId,sourceNet,rHost, **kwargs):
    redmine = Redmine(rmUrl, key=rmKey)
    issue = redmine.issue.new()
    issue.project_id = rmProjectId
    issue.subject = rmIssueSubj
    issue.tracker_id = 9
    issue.description = rmIssueDesc
#    issue.status_id = 3
    issue.priority_id = 3
#    issue.assigned_to_id = 123
    issue.custom_fields = [{'id': 2, 'value': sessId}, {'id': 3, 'value': sourceNet}, {'id': 5, 'value': rHost}]
    issue.save()
    loginTicket = issue.id
    return loginTicket

def slackNotifySucess(slackChannel,botUser,slackNotFallBack,slackNotText,loginUser,loginTicket,rHost,sourceNet,colorCode):
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
                "title": "Login Ticket",
                "value": "<"+rmUrl+"/issues/"+str(loginTicket)+"|"+str(loginTicket)+">",
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

def slackNotifySshCmd(slackChannel,botUser,slackNotFallBackCmd,slackNotTextCmd,loginUser,loginTicket,rHost,sourceNet,colorCode):
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
        "fallback": slackNotFallBackCmd,
        "text": slackNotTextCmd,
        "fields": [{
                "title": "User",
                "value": loginUser,
                "short": "true"
        }, {
                "title": "Command",
                "value": sshOrigCmd,
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

def ophoisLoginLogs(loggingFile,loggingType):
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
            loginTicket) + '] ' '[' + str(loginUser) + '] ' '[' + str(rHost) + '] ' '[ophois-login-event] ' '[%(funcName)s] ' '[%(message)s]')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger, handler, formatter

def ophLogin():
    loggingType = "login"
    fileName = open(loginTicketDir + "/" + str(loginTicket), "w")
    fileName.write(sessId)
    fileName.close()
    ophoisLoginLogs(loggingFile, loggingType)
    logger.info('OPHOIS SSH login sucess')
    exitStatus = (os.system(cmd))
    if exitStatus == ("0"):
        ophoisLoginLogs(loggingFile)
        logger.info('OPHOIS SSH login failed')
    return exitStatus

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
cmd = "/bin/ophrec "+logDir+"/"+logFile+"_"+sessId+".oph"

if rHost is not re.compile('172.24.1.*'):
    sourceNet = "NON-DMZ"

if sourceNet == ("DMZ"):
    colorCode = "#008000"
    botUser = "OPHOIS Login Alert"

if os.environ.get('SSH_ORIGINAL_COMMAND') is not None:
    colorCode = "#ff0000"
    botUser = "OPHOIS Security Alert"
    slackNotifySshCmd(slackChannel, botUser,slackNotFallBackCmd, slackNotTextCmd, loginUser, rHost, sourceNet,botUser)
    sys.exit()

if "scp" in os.environ:
    print 'In order to use copy funstionality please use #jcp tool or Contact administrator'
    print '################################################################'
    print '#           Requet deny by OPHOIS SSH Gateway                  #'
    print '#        OPHOIS supports interactive sessions only             #'
    print '#                Do not supply a command                       #'
    print '#   In order to use copy funstionality please use #jcp tool    #'
    print '################################################################'
    colorCode = "#ff0000"
    botUser = "OPHOIS Security Alert"
    slackNotifySshCmd(slackChannel,botUser,slackNotFallBackCmd,slackNotTextCmd,loginUser,rHost,sourceNet,botUser)
    sys.exit()
if redmineNotify == ("Yes"):
   loginTicket = createLoginTicket(rmUrl,rmKey,rmProjectId,rmIssueSubj,rmIssueDesc,sessId,sourceNet,rHost)
   os.environ['ticket'] = str(loginTicket)
else:
   print "Login tickets  disabled"

os.environ['sessId'] = sessId
if slackNotify == ("Yes"):
   slackNotifySucess(slackChannel,botUser,slackNotFallBack,slackNotText,loginUser,loginTicket,rHost,sourceNet,colorCode)
else:
   print "Slack notification disabled"

print '                     -`    `                                    '
print '                     -h+   oy`                                  '
print '                     `ysh. -hh+                                 '
print '                     /y:h+ shhh-                                '
print '                     yo-hh.hhhho                                '
print '                     ho-hhyhhhhh.                               '
print '                    `dhshhhhhhhhs-.                             '
print '                 `/ymmddhhhhddddhddy+:----.```                  '
print '               :yNNNNNNNNmhhhdhhyhdshhhyyyyyyyys+               '
print '            `odNNNNNNNNNNNmdhhhhhhhhhhhhhhhhhhy/                '
print '          `sNNNNNNNNNNNNNNNNmmdhhhhyo+++/::::.`                 '
print '         :mNNNNNNNNNNNNNNNNNNmdhhhdd+                           '
print '        /NNNNNNNNNNNNNNNNNNNNmhhhdmmmh-``                       '
print '        mNNNNNNmmhdhdysdNNNNNmhddmNNNmmdhhyyo/-`                '
print '        NNmmmmmmmmhhhyddNNNNNdyyshNNNNNhdddddddhs-              '
print '        NmmmmmmmmmmdhhddNNNNNdmydhNNNNNmdmdddddddd/`            '
print '        NmmmmmmmmmmmmmhhNNNNNhm+dmNNNNNmdddmdddddds`            '
print '        mdddddddmmmmmmmmNNNNNmddmmNNNNNmdmmhyhyyyys             '
print '        oyyyyyhy:dmmmmmmdddhdmmmmmhhhhdmmmo:yyyyyyy.            '
print '        :mmmmmmd `smmmmmmmmmmmmmmmmmmmmmmd.`ddddddd+            '
print '        -mmmmmmd  `+mmmmmmmmmmmmmmmmmmmmmo  yddddddh`           '
print '        .mmmmmmd`   /mmmmmmmmmmmmmmmmmmmd`  /mdddddd:           '
print '        .mmmmmmd`    smmmmmmmmmmmmmmmmmms   -mdddddd+           '
print '        .mmmmmmd`    .ddmmmmmmmmmmmmmmmm/   `dddddddy           '
print '        `mmmmmmd     -dddmddmmmmmmmmmmmm-    sdmmmddd`          '
print '        -mmmmmmd     ymmddmdddmmmmmmmmmm:    /mmmmddm-          '
print '        :mmmmmmd    oyyyyyhhdddddddmmmmm+    .mmmmmmm/          '
print '        .///////`  .:::::::::::::///////:     ///////-          '
print '                                                                '
print '################################################################'
print '#             Welcome to OPHOIS SSH Gateway                    #'
print '#       All connections are monitored and recorded             #'
print '#   Disconnect IMMEDIATELY if you are not an authorized user!  #'
print '################################################################'
print 'AUDIT KEY: ' +logFile

ophLogin()