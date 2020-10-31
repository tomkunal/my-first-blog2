import os
import json
import re
from .models import SiriusSubmissionGroup,SiriusSubmission,SiriusSubmissionConfigData,SiriusJobTable

sub_group_id = "1"
sub_id       = "1"

def getMachineNameFromString(multipleMachineNamesString, delimeter = ";"):
    machineNamesList = multipleMachineNamesString.split(delimeter)
    machineNamesList = list(filter(None, machineNamesList))
    return machineNamesList

# def getUser(request):
#     client_ip = request.environ.get('REMOTE_ADDR')
#     print ('client_ip:', client_ip)
#     userRsp = GetUserNameFromIP(client_ip)
#     return  userRsp

def get_default_config_data():
  config_data = dict()
  config_data["WBTSanityLocation"]   = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="WBTSanityLocation").data_value
  config_data["WBTTestName"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="WBTTestName").data_value
  config_data["WBTTestCommand"]      = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="WBTTestCommand").data_value
  config_data["PlugInFiles"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="PlugInFiles").data_value
  config_data["ConfigFiles"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="ConfigFiles").data_value
  config_data["IsDirectory"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="IsDirectory").data_value
  config_data["CopyDST"]             = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="CopyDST").data_value
  config_data["UpdateDllOnly"]       = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="UpdateDllOnly").data_value
  config_data["lstDrvBranch"]           = json.dumps(os.listdir(r"\\builds\nightly\displaySanity"))
  config_data["DrvBranch"]           = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="DrvBranch").data_value
  config_data["SatSunRun"]           = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="SatSunRun").data_value
  config_data["RunInLoops"]          = "0" #SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="RunInLoops").data_value[0]
  config_data["CopyResultTo"]        = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="CopyResultTo").data_value
  config_data["UserName"]            = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="UserName").data_value
  config_data["SendMailCC"]          = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="SendMailCC").data_value
  config_data["SendMailTo"]          = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="SendMailTo").data_value
  config_data["StagingBits"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="StagingBits").data_value
  config_data["StagingPath"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="SpiderService", data_key="StagingPath").data_value
  #print ("ConfigData", configData)
#// start time end time execute default
  return config_data

def get_default_driver_install_data():
  driver_install_data = dict()
  driver_install_data["DrvLocation"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="DriverInstall", data_key="DrvLocation").data_value  
  driver_install_data["DrvShare"]            = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="DriverInstall", data_key="DrvShare").data_value
  driver_install_data["DrvVer"]              = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="DriverInstall", data_key="DrvVer").data_value
  driver_install_data["DrvPath"]             = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="DriverInstall", data_key="DrvPath").data_value
  driver_install_data["DrvBranchInstall"]    = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="DriverInstall", data_key="DrvBranchInstall").data_value
  driver_install_data["SysType"]             = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="DriverInstall", data_key="SysType").data_value
  driver_install_data["FolderSize"]          = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="DriverInstall", data_key="FolderSize").data_value
  driver_install_data["CleanInstall"]        = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="DriverInstall", data_key="CleanInstall").data_value
  driver_install_data["Execute"]             = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="DriverInstall", data_key="Execute").data_value
  #print ("driver_install_data", driver_install_data)
  return driver_install_data


def get_default_gfe_install_data():
  gfe_install_data = dict()
  gfe_install_data["BaseDir"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="GFEInstall", data_key="BaseDir").data_value
  gfe_install_data["Branch"]          = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="GFEInstall", data_key="Branch").data_value
  gfe_install_data["Version"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="GFEInstall", data_key="Version").data_value
  gfe_install_data["Delay"]           = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="GFEInstall", data_key="Delay").data_value
  gfe_install_data["Respond_To_EULA"] = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="GFEInstall", data_key="Respond_To_EULA").data_value
  gfe_install_data["GFE_CleanInstall"]    = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="GFEInstall", data_key="CleanInstall").data_value
  gfe_install_data["InstallLogsDir"]  = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="GFEInstall", data_key="InstallLogsDir").data_value
  gfe_install_data["GFE_Execute"]         = SiriusSubmissionConfigData.objects.using('spider_db').get(submission_group_id=sub_group_id, submission_id=sub_id, data_type="GFEInstall", data_key="Execute").data_value
  return gfe_install_data


# def GetUserNameFromIP(ip):
#     try:
#         cmd = "ping -n 1 -a " + ip
#         process = os.popen(cmd)
#         responseText = process.read()
#         print ('responseText :', responseText)
#         process.close()
#         user = re.findall(r"((\w){2,}(-LT))",responseText)[0][0]
#         print ("user", user)
#         user = re.finda1ll(r"((\w){2,})",user)[0][0]
#         print ("user2", user)
#         return [True, user]
#     except Exception as e:
#         print('Exception: ', str(e), ip)
#         return [False, str(e)]
