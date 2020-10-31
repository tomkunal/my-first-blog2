
import csv
import datetime
import json
import os
import uuid

#import ldap
import numpy as np
import pandas as pd
from django.core import serializers
from django.db import connection, connections
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect
#from django_pandas.io import read_frame

#import pyodbc
import base64
#from SqlDBUtil import SqlDBUtil

#from . import utils
#from .import templatetree

from .models import (SiriusJobTable, SiriusSubmission,
                     SiriusSubmissionConfigData, SiriusSubmissionGroup,
                     SiriusTaskInfo, Testtempfolderinfo, Testtempfoldertree)

jsonSpiderCommon = {}
# cacheFilePath = "D:\\DjangoProjects\\csv\\devtestDBcheck\\GetData\\json.txt"
cacheFilePath = "C:\\data\\json.txt"


def load_tree(request):
    flag = request.GET.get('refreshdata')
    jsondata = templatetree.get_cache_data(flag)
    return JsonResponse(jsondata, safe=False)


def get_submission_group_table(request):
    username = request.GET.get('username')
    print(username)
    if username == 'hlahoti' or username == 'amity' or username == 'hchopde':
        query = """SELECT TOP 100 [Submission_Group_Id],[Submission_Group_Name],[Submission_Group_Status]
                ,[Submission_Test_Type],[Machine],[Requester],[Priority]
                    FROM [Experi1].[dbo].[Sirius_Submission_Group] WITH(NOLOCK)
                    order by Submission_Group_Id desc """
    elif username != None:
        query = """SELECT TOP 40 [Submission_Group_Id],[Submission_Group_Name],[Submission_Group_Status]
                    ,[Submission_Test_Type],[Machine],[Requester],[Priority]
                        FROM [Experi1].[dbo].[Sirius_Submission_Group] WITH(NOLOCK)
                        where [Requester] = '{0}' order by Submission_Group_Id desc """.format(username)

    with connections['spider_db'].cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchall()
        listofdata = [list(x) for x in row]
    if(row):
        get_result_table_df = pd.DataFrame(listofdata)
        get_result_table_df.fillna(value="-123", inplace=True)
        get_result_table_df.columns = ['Submission_Group_Id', 'Submission_Group_Name',
                                       'Submission_Group_Status', 'Submission_Test_Type', 'Machine', 'Requester', 'Priority']
        jsondata = get_result_table_df.to_json(orient='records')
        jsondata = json.loads(jsondata)
    else:
        jsondata = {}

    return JsonResponse(jsondata, safe=False)


def get_result_table(request):
    submission_group_id = request.GET.get('submissionGroupId')
    query = """ SELECT TOP 1000 [Submission_Group_Id],SJT.[Submission_Id],
    SJT.[Job_Id],[Job_Status] ,[Template_Id],[Task_Id]
    ,[Sequence] ,[Root_Folder] ,[Job_Start_Time],
    [Job_End_Time],[Job_Result] ,[BugId],[ResultPath] FROM [Experi1].[dbo].[Sirius_Job_Table] SJT
    left join [Experi1].[dbo].[Sirius_Submission] SS
    on SJT.[Submission_Id] = SS.[Submission_Id]  Left join [Experi1].[dbo].[LAT_Analysis_Information] LAT on
    SJT.[BAT_Analysis_Id] = LAT.[id]  Left join [Experi1].[dbo].[Sirius_Task_Info] STI
    on SJT.[Job_Id] = STI.[Job_Id]
    where [Submission_Group_Id] in ({}) """.format(submission_group_id)
    status, get_result_table_df = SqlDBUtil.execute_select_query_get_df2(
        query, SqlDBUtil.IT_PROD_SQL174)

    if(status):

        get_result_table_df.columns = ['Submission_Group_Id', 'Submission_Id', 'Job_Id', 'Job_Status',
                                       'Template_Id', 'Task_Id', 'Sequence', 'Root_Folder', 'Job_Start_Time',
                                       'Job_End_Time', 'Job_Result', 'BugId', 'ResultPath']
        get_result_table_df['BugId'].fillna(value=-2, inplace=True)
        get_result_table_df.fillna(value="NA", inplace=True)

        get_result_table_df['BugId'] = get_result_table_df['BugId'].apply(
            lambda x: 'http://nvbugs//{}'.format(x) if x > 100 else "NA")

        get_result_table_df['ResultPath'] = get_result_table_df['ResultPath'].apply(
            lambda x: x + '\\TestResultDetails.html' if x != "NA" else "NA")
        get_result_table_df['ResultPath'] = get_result_table_df['ResultPath'].replace(
            "\\", "//")
        # get_result_table_df['ResultPath'] = get_result_table_df['ResultPath'].apply(lambda x: '<a href=file:{0}">LogsLocation</a>'.format(x))

        jsondata = get_result_table_df.to_json(orient='records')
        jsondata = json.loads(jsondata)
    else:
        jsondata = {}
    return JsonResponse(jsondata, safe=False)


def get_all_submission_for_submission_group(request):
    submission_group_id = request.GET.get('submission_group_id')
    query = """ SELECT Distinct [Submission_Group_Id],SS.[Submission_Id],[Test_Config_File_Path]
        ,[Submission_Status]
      ,[Submission_Time],[Submission_Started_Time],[Submission_Finished_Time]
      ,[Resubmitted]
	  ,[Root_Folder] 
	  FROM [Experi1].[dbo].[Sirius_Submission] SS
     left join[Experi1].[dbo].[Sirius_Job_Table] SJT
    on SS.[Submission_Id] = SJT.[Submission_Id]
       where [Submission_Group_Id] in ({}) """.format(submission_group_id)
    status, get_submission_table_df = SqlDBUtil.execute_select_query_get_df2(
        query, SqlDBUtil.IT_PROD_SQL174)

    if(status):

        get_submission_table_df.columns = ['Submission_Group_Id', 'Submission_Id', 'Test_Config_File_Path', 'Submission_Status',
                                           'Submission_Time', 'Submission_Started_Time', 'Submission_Finished_Time', 'Resubmitted',
                                           'TemplateFolderpath']
        get_submission_table_df.fillna(value="NA", inplace=True)
        jsondata = get_submission_table_df.to_json(orient='records')
        jsondata = json.loads(jsondata)
    else:
        jsondata = {}
    return JsonResponse(jsondata, safe=False)


def get_all_submission_name(request):
    username = request.GET.get('username')
    with connections['spider_db'].cursor() as cursor:
        query = """SELECT TOP 40 [Submission_Group_Id],[Submission_Group_Name] FROM [Experi1].[dbo].[Sirius_Submission_Group] WITH(NOLOCK)
                        where [Requester] = '{0}' order by Submission_Group_Id desc """.format(username)

        cursor.execute(query)
        row = cursor.fetchall()
        listofdata = [list(x) for x in row]

    return JsonResponse(listofdata, safe=False)


def get_all_job_for_submission(request):
    submission_group_id = request.GET.get('submission_group_id')
    query = """ SELECT SJT.[Submission_Id],
    SJT.[Job_Id],[Job_Status] ,[Template_Id],
    [Sequence] ,[Root_Folder] ,[Job_Start_Time],
    [Job_End_Time],[Job_Result] FROM [Experi1].[dbo].[Sirius_Job_Table] SJT
    left join [Experi1].[dbo].[Sirius_Submission] SS
    on SJT.[Submission_Id] = SS.[Submission_Id]
    where [Submission_Group_Id] in ({}) """.format(submission_group_id)

    status, get_result_table_df = SqlDBUtil.execute_select_query_get_df2(
        query, SqlDBUtil.IT_PROD_SQL174)

    if(status):

        get_result_table_df.columns = ['Submission_Id', 'Job_Id', 'Job_Status',
                                       'Template Id', 'Feature sequence', 'TemplateFolderpath', 'Job_Start_Time',
                                       'Job_End_Time', 'Job_Result']
        get_result_table_df.fillna(value="NA", inplace=True)

        jsondata = get_result_table_df.to_json(orient='records')
        jsondata = json.loads(jsondata)
    else:
        jsondata = {}
    return JsonResponse(jsondata, safe=False)


def login(request):
    usrname = request.GET.get('username')
    data = base64.b64decode(usrname)
    username = data.decode()
    try:
        query = f"SELECT count([NTAccount]) FROM [NVBugsDW].[dbo].[User] where [NTAccount] = '{username}' and IsActive = 1"
        connection = pyodbc.connect(SqlDBUtil.GremlinLink)
        crs = connection.cursor()
        crs.execute(query)
        result = crs.fetchall()
        result =  [list(r) for r in result]
        del crs
        connection.close()
        result =  [list(r) for r in result]
        if result >= [[1]]:
            return JsonResponse('Authorized', status=200, safe=False)
        return JsonResponse('Unauthorized', status=401, safe=False)
    except Exception as e:
        return JsonResponse('Unauthorized' + e, status=401, safe=False)
    


def load_task(request):
  #  request.POST.get('requester')
    requester = jsonSpiderCommon["requester"]
    release = jsonSpiderCommon["Release"]

    devtest_task_query = """SELECT  [ProjectID],[IssueID],[TestTemplateID],[IssueTitle]
                         ,[EnvironmentInfo],FieldVarcharLong7,
                         DevtestDB2.dbo.GetTestTempFolderPath(1072,TestTemplateID,TestTaskFolderID) as TempFolderPath
                         FROM [DevtestDB2].[dbo].[TestTaskGeneralInfo] WITH(NOLOCK)
                         where ProjectID = '{}' and  IfClosed = 0 and [FieldVarcharLong7] is not NULL and
                         CrntOwnerID in (SELECT [LoginID] FROM [DevtestDB2].[dbo].[LoginAccount] WITH(NOLOCK)
                         where LoginName ='{}')""".format(release, requester)

    status, devtest_task_df = SqlDBUtil.execute_select_query_get_df2(
        devtest_task_query, SqlDBUtil.DevTestLink)
    if status:
        devtest_task_df.columns = ['Project_ID', 'Task_Id', 'Template_ID',
                                   'issuetitle', 'EnvironmentInfo', 'Feature_Sequence', 'TemplateFolderpath']
        devtest_task_df['TemplateFolderpath'] = devtest_task_df['TemplateFolderpath'].str.replace(
            '\\', '\\\\')
        devtest_task_df['jobid'] = 0
        condition_df = devtest_task_df[['Project_ID', 'Task_Id']]
        status, whereclause = SqlDBUtil.generate_where_clause_string(
            condition_df)
        if status:
            task_already_created_query = "SELECT TOP 1000 [Task_Id]  FROM [Experi1].[dbo].[Sirius_Task_Info] where " + " OR ".join(
                whereclause)
            status, task_created_df = SqlDBUtil.execute_select_query_get_df2(
                task_already_created_query, SqlDBUtil.IT_PROD_SQL174)
            if status:
                devtest_task_df = devtest_task_df[~devtest_task_df.Task_Id.isin(
                    task_created_df.Task_Id)]
            else:
                jsondata = {}
        else:
            jsondata = {}

        jsondata = devtest_task_df.to_json(orient='records')
        jsondata = json.loads(jsondata)
    else:
        jsondata = {}

    return JsonResponse(jsondata, safe=False)


def load_template(request):
    folder_id = request.GET.getlist('folderIds')
    feature_part = request.GET.get('featurePart')
    template_part = request.GET.get('templatePart')
    print("template_part : " ,template_part)
    whattodo = request.GET.get('whattoDo')

    folder_id = str(folder_id)
    folder_id = folder_id.replace('[', '')
    folder_id = folder_id.replace(']', '')
    with connection.cursor() as cursor:
        var = "SELECT  IssueId  as TemplateId,dbo.GetTestTempFolderPath(1072, IssueId, ''), IssueTitle,TTGI.FieldInt10,TTGI.FieldVarcharLong12,TTGI.[IsActive]\
       FROM TestTempGeneralInfo TTGI WITH(NOLOCK) WHERE TTGI.ProjectID = 1072  AND TTGI.FieldInt10= 1 AND TTGI.FieldVarcharLong12 IS NOT NULL \
       AND (TTGI.TestTempFolderId IN ({0}) or IssueId in ({1}))".format(folder_id,template_part)
        print(var)
        cursor.execute(var)
        row = cursor.fetchall()

    if(row):
        get_templates_for_folder = pd.DataFrame(row)
        get_templates_for_folder.columns = [
            'IssueId', 'TemplateFolderpath', 'issuetitle', 'fieldint10', 'fieldvarcharlong12', 'IsActive']
        get_templates_for_folder['TemplateFolderpath'] = get_templates_for_folder['TemplateFolderpath'].str.replace(
            '\\', '\\\\')
        get_templates_for_folder['IsActive'] = get_templates_for_folder['IsActive'].replace(
            1, 'Active')
        get_templates_for_folder['IsActive'] = get_templates_for_folder['IsActive'].replace(
            0, 'Inactive')

        get_templates_for_folder['jobid'] = 0
        get_templates_for_folder = get_templates_for_folder[~get_templates_for_folder['fieldvarcharlong12'].str.startswith('W', na=False)]
        if whattodo == "1":  # remove certain feature
            print('remove')
            get_templates_for_folder = get_templates_for_folder[get_templates_for_folder['fieldvarcharlong12'].str.contains(
                feature_part) == False]
        if whattodo == "-1":  # only this feature to be removd
            print('only')
            get_templates_for_folder = get_templates_for_folder[get_templates_for_folder['fieldvarcharlong12'].str.contains(
                feature_part)]

        jsondata = get_templates_for_folder.to_json(orient='records')
    else:
        jsondata = {}
    return JsonResponse(jsondata, safe=False)

def timekunal(request):
    feature_part = request.GET.get('featurePart')
    print(feature_part)
    return JsonResponse("kunal", safe=False)

def know_feature(request):
    feature_part = request.GET.get('featurePart')
    if feature_part.find("-"):
        feature_part_array = feature_part.split('-')
        featurename = ""
    with open("\\\\netapp-pu02\\gpu_qa_pu\\public\\White_Box_Testing\\DriverStackSanity\\FeatureMapTables\\FeatureMapTable.csv") as f:
        reader = csv.reader(f)
        your_list = list(reader)
    for k in feature_part_array:
        for i in your_list:
            for j in i:
                if k == j:
                    featurename += i[0] + " " + i[1] + " \n"
    if featurename == "":
        featurename = "enter proper string"

    print("feature name :" + featurename)
    return JsonResponse(featurename, safe=False)


def render_result_page(request):
    return render(request, 'GetData/Result.html')

def render_game(request):
    return render(request, 'GetData/index.html')

def render_resubmit_page(request):
    return render(request, 'GetData/Resubmit.html')


def render_task_page(request):
    return render(request, 'GetData/LoadTask.html')


def render_nested_page(request):
    return render(request, 'GetData/nestedGrid.html')


def render_start_page(request):
    return render(request, 'GetData/startPage.html')


def render_page(request):
    return render(request, 'GetData/home2.html')


# Sirius Functions

def json_output(status, message):
    res_dict = {}
    res_dict['Status'] = status
    res_dict['Message'] = message
    json_data = json.dumps(res_dict)
    return (json_data)


def get_basic_info(request):
    jsonSpiderCommon["submission_group_name"] = request.POST.get(
        'submission_group_name')
    jsonSpiderCommon["submission_owner"] = request.POST.get('submission_owner')
    jsonSpiderCommon["priority"] = request.POST.get('priority')
    jsonSpiderCommon["machine"] = utils.getMachineNameFromString(
        request.POST.get('machine'), ";")
    jsonSpiderCommon["requester"] = request.POST.get('requester')
    jsonSpiderCommon["SendMailTo"] = request.POST.get('sendMailTo')
    jsonSpiderCommon["alias"] = request.POST.get('alias')
    if jsonSpiderCommon["alias"] == "":
        jsonSpiderCommon["alias"] = None
    jsonSpiderCommon["starred"] = "0"
    jsonSpiderCommon["submission_test_type"] = "Spider"
    jsonSpiderCommon['username'] = jsonSpiderCommon["requester"]

    jsonSpiderCommon["test_config_file_path"] = request.POST.get(
        'test_config_file_path')
    jsonSpiderCommon["devtest_update_path"] = "none"
    jsonSpiderCommon["Release"] = request.POST.get('ReleaseValue_ID')
    jsonSpiderCommon["SendMailCC"] = jsonSpiderCommon["alias"]
    if jsonSpiderCommon["SendMailTo"] == "none":
        jsonSpiderCommon["SendMailTo"] = jsonSpiderCommon["requester"]
    jsonSpiderCommon["data_type"] = "SpiderService"


def get_spider_service_data(request):
    config_data_default = utils.get_default_config_data()
    config_data_key = ["PlugInFiles",
                       "ConfigFiles",
                       "CopyDST",
                       "UpdateDllOnly",
                       "DrvBranch",
                       "SatSunRun",
                       "RunInLoops",
                       "CopyResultTo",
                       "StagingBits",
                       "StagingPath"]
    spider_service_data = dict()
    for config_key in config_data_key:
        if str(request.POST.get(config_key)) != config_data_default[config_key]:
            # print ("config_key:",config_key,"ConfigValue",request.POST.get(config_key))
            spider_service_data[config_key] = request.POST.get(config_key, 0)

    jsonSpiderCommon["SpiderService"] = spider_service_data


def get_driver_install_data(request):
    driver_install_default = utils.get_default_driver_install_data()
    config_data_key = ["DrvLocation",
                       "DrvShare",
                       "DrvVer",
                       "DrvPath",
                       "DrvBranchInstall",
                       "SysType",
                       "FolderSize",
                       "CleanInstall",
                       "Execute"]
    spider_service_data = dict()
    for config_key in config_data_key:
        if str(request.POST.get(config_key)) != driver_install_default[config_key]:
            # print ("config_key:",config_key,"ConfigValue",request.POST.get(config_key))
            spider_service_data[config_key] = request.POST.get(config_key, 0)
    jsonSpiderCommon["DriverInstall"] = spider_service_data


def get_gfe_install_data(request):
    gfe_install_default = utils.get_default_gfe_install_data()
    config_data_key = ["BaseDir",
                       "Branch",
                       "Version",
                       "Delay",
                       "Respond_To_EULA",
                       "GFE_CleanInstall",
                       "InstallLogsDir",
                       "GFE_Execute"]
    spider_service_data = dict()
    for config_key in config_data_key:
        if str(request.POST.get(config_key)) != gfe_install_default[config_key]:
            # print ("config_key:",config_key,"ConfigValue",request.POST.get(config_key))
            spider_service_data[config_key] = request.POST.get(config_key, 0)
    jsonSpiderCommon["GFEInstall"] = spider_service_data


def add_data_sirius_submission_group(machine_name, jsonSpiderCommon):
    try:
        obj_srius_submission_group = SiriusSubmissionGroup()
        obj_srius_submission_group.submission_group_name = jsonSpiderCommon[
            "submission_group_name"]
        obj_srius_submission_group.submission_owner = jsonSpiderCommon["submission_owner"]
        obj_srius_submission_group.priority = jsonSpiderCommon["priority"]
        # jsonSpiderCommon["machine"]
        obj_srius_submission_group.machine = machine_name
        obj_srius_submission_group.requester = jsonSpiderCommon["requester"]
        obj_srius_submission_group.alias = jsonSpiderCommon["alias"]
        obj_srius_submission_group.starred = jsonSpiderCommon["starred"]
        obj_srius_submission_group.submission_test_type = jsonSpiderCommon[
            "submission_test_type"]
        obj_srius_submission_group.submission_group_status = ""
        obj_srius_submission_group.save(using='spider_db')
    except Exception as error:
        print(error)
        return False, str(error)


def add_data_sirius_submission_config_data(current_sirius_submission_group, current_sirius_submission, json_doc):

    config_data_key = ["PlugInFiles", "ConfigFiles", "CopyDST", "UpdateDllOnly", "DrvBranch", "SatSunRun",
                       "RunInLoops", "CopyResultTo", "StagingBits", "StagingPath"]

    driver_data_key = ["DrvLocation", "DrvShare", "DrvVer", "DrvPath", "DrvBranchInstall", "SysType",
                       "FolderSize", "CleanInstall", "Execute"]

    gfe_data_key = ["BaseDir", "Branch", "Version", "Delay",
                    "Respond_To_EULA", "GFE_CleanInstall", "InstallLogsDir", "GFE_Execute"]

    spider_service_data = jsonSpiderCommon["SpiderService"]

    for config_key in spider_service_data:
        if config_key in config_data_key:
            obj_sirius_submission_config_data = SiriusSubmissionConfigData()
            # ID From Submission Group Table
            obj_sirius_submission_config_data.submission_group_id = current_sirius_submission_group.submission_group_id
            # ID From Submission Table
            obj_sirius_submission_config_data.submission_id = current_sirius_submission.submission_id
            obj_sirius_submission_config_data.data_type = "SpiderService"
            obj_sirius_submission_config_data.data_key = config_key
            # request.POST.get(config_key, 0)
            obj_sirius_submission_config_data.data_value = spider_service_data[config_key]
            obj_sirius_submission_config_data.save(using='spider_db')
            # print ("SiriusSubmissionConfigData saved")

    # WBTTestCommand, Sanity location and WBTTestname IsDirectory Execute default
    obj_sirius_submission_config_data = SiriusSubmissionConfigData()
    # ID From Submission Group Table
    obj_sirius_submission_config_data.submission_group_id = current_sirius_submission_group.submission_group_id
    # ID From Submission Table
    obj_sirius_submission_config_data.submission_id = current_sirius_submission.submission_id
    obj_sirius_submission_config_data.data_type = "SpiderService"
    obj_sirius_submission_config_data.data_key = "UserName"
    obj_sirius_submission_config_data.data_value = jsonSpiderCommon["requester"]
    obj_sirius_submission_config_data.save(using='spider_db')
    obj_sirius_submission_config_data = SiriusSubmissionConfigData()
    # ID From Submission Group Table
    obj_sirius_submission_config_data.submission_group_id = current_sirius_submission_group.submission_group_id
    # ID From Submission Table
    obj_sirius_submission_config_data.submission_id = current_sirius_submission.submission_id
    obj_sirius_submission_config_data.data_type = "SpiderService"
    obj_sirius_submission_config_data.data_key = "SendMailTo"
    obj_sirius_submission_config_data.data_value = jsonSpiderCommon["SendMailTo"]
    obj_sirius_submission_config_data.save(using='spider_db')

    obj_sirius_submission_config_data = SiriusSubmissionConfigData()
    # ID From Submission Group Table
    obj_sirius_submission_config_data.submission_group_id = current_sirius_submission_group.submission_group_id
    # ID From Submission Table
    obj_sirius_submission_config_data.submission_id = current_sirius_submission.submission_id
    obj_sirius_submission_config_data.data_type = "SpiderService"
    obj_sirius_submission_config_data.data_key = "SendMailCC"
    obj_sirius_submission_config_data.data_value = jsonSpiderCommon["SendMailCC"]
    obj_sirius_submission_config_data.save(using='spider_db')
    # print ("SiriusSubmissionConfigData saved")

    driver_install_data = jsonSpiderCommon["DriverInstall"]

    for config_key in driver_install_data:
        if config_key in driver_data_key:
            # if DefDriverDataVal[config_key] != driver_install_data[config_key]:
            obj_sirius_submission_config_data = SiriusSubmissionConfigData()
            # ID From Submission Group Table
            obj_sirius_submission_config_data.submission_group_id = current_sirius_submission_group.submission_group_id
            # ID From Submission Table
            obj_sirius_submission_config_data.submission_id = current_sirius_submission.submission_id
            obj_sirius_submission_config_data.data_type = "DriverInstall"
            obj_sirius_submission_config_data.data_key = config_key
            obj_sirius_submission_config_data.data_value = driver_install_data[config_key]
            obj_sirius_submission_config_data.save(using='spider_db')
            # print ("SiriusSubmissionConfigData Driver Install saved")

    gfe_install_data = jsonSpiderCommon["GFEInstall"]

    for config_key in gfe_install_data:
        if config_key in gfe_data_key:
            # if DefGFEDataVal[config_key] != gfe_install_data[config_key]:
            obj_sirius_submission_config_data = SiriusSubmissionConfigData()
            # ID From Submission Group Table
            obj_sirius_submission_config_data.submission_group_id = current_sirius_submission_group.submission_group_id
            # ID From Submission Table
            obj_sirius_submission_config_data.submission_id = current_sirius_submission.submission_id
            obj_sirius_submission_config_data.data_type = "GFEInstall"
            obj_sirius_submission_config_data.data_key = config_key
            obj_sirius_submission_config_data.data_value = gfe_install_data[config_key]
            obj_sirius_submission_config_data.save(using='spider_db')

def add_data_sirus_task_info(json_doc, job_guid):
    try:
        sirius_job_submission = SiriusJobTable.objects.using(
            'spider_db').filter(job_guid__iexact=job_guid)
        lst_job_submission = list(sirius_job_submission)
        print("jobID", lst_job_submission[0].job_id)
        if(len(lst_job_submission) > 0):
            obj_sirius_task_info = SiriusTaskInfo()
            obj_sirius_task_info.task_id = json_doc["Task Id"]
            obj_sirius_task_info.job_id = lst_job_submission[0].job_id
            obj_sirius_task_info.project_id = json_doc["Project Id"]
            obj_sirius_task_info.task_create_update_info = "TASK_ALREADY_CREATED"
            obj_sirius_task_info.last_modified = datetime.datetime.now()
            obj_sirius_task_info.save(using='spider_db')
    except Exception as error:
        print(error)
        return False, str(error)


def add_data_database(request, current_sirius_submission_group):
    try:
        str_json_seq = request.POST.get('json_seq', None)
        location = request.POST.get('location', None)
        json_seq = json.loads(str_json_seq)
        is_any_spidertestsub_machine = False

        old_doc = None
        current_sirius_submission = None
        new_sirius_submission = False
        json_seq = sorted(json_seq, key=lambda x: x['TemplateFolderpath'])

        for json_doc in json_seq:
            # print ("JSON DOC", json_doc)
            if old_doc is not None:
                if old_doc["TemplateFolderpath"] != json_doc["TemplateFolderpath"]:
                    new_sirius_submission = True
            else:
                new_sirius_submission = True

            if new_sirius_submission:
                print("new_Submission")
                # Submission Table
                obj_sirius_submission = SiriusSubmission()
                # ID From Submission Group Table
                obj_sirius_submission .submission_group_id = current_sirius_submission_group.submission_group_id
                obj_sirius_submission .test_config_file_path = jsonSpiderCommon[
                    "test_config_file_path"]
                obj_sirius_submission .devtest_update_path = jsonSpiderCommon["devtest_update_path"]
                obj_sirius_submission .save(using='spider_db')

                # print ("SiriusSubmission saved")

                # Submission Config Data Table
                current_sirius_submission = SiriusSubmission.objects.using(
                    'spider_db').all().order_by("-submission_id")[0]

                if not is_any_spidertestsub_machine:
                    add_data_sirius_submission_config_data(
                        current_sirius_submission_group, current_sirius_submission, json_doc)

                    # print ("SiriusSubmissionConfigData GFE Install saved")
            job_guid = str(uuid.uuid4())
            # Job Table
            obj_sirius_job_table = SiriusJobTable()
            # ID From Submission Table
            obj_sirius_job_table.submission_id = current_sirius_submission.submission_id
            obj_sirius_job_table.template_id = json_doc["Template Id"]
            obj_sirius_job_table.sequence = json_doc["Feature sequence"]
            obj_sirius_job_table.job_guid = job_guid
            # root_folder -> template folder path - Nvidia Root Folder
            # file_name   -> last folder name
            if json_doc["TemplateFolderpath"].find('\\\\Nvidia Root Folder\\\\') != -1:
                root_folder = json_doc["TemplateFolderpath"][json_doc["TemplateFolderpath"].rindex(
                    '\\\\Nvidia Root Folder\\\\')+22:]
            else:
                root_folder = json_doc["TemplateFolderpath"]

            print('root_folder', root_folder)
            obj_sirius_job_table.root_folder = escape_special_char_folder(
                root_folder)

            obj_sirius_job_table.file_name = escape_special_char_folder(
                json_doc["TemplateFolderpath"][json_doc["TemplateFolderpath"].rindex('\\')+1:])
            obj_sirius_job_table.save(using='spider_db')

            if(location == "taskview" and json_doc["Task Id"] != ""):
                add_data_sirus_task_info(json_doc, job_guid)

            # print ("SiriusJobTable saved")
            old_doc = json_doc
            if not is_any_spidertestsub_machine and jsonSpiderCommon["submission_test_type"] == 'Spider':
                is_any_spidertestsub_machine = True
            new_sirius_submission = False

    except Exception as error:
        print(error)
        return False, str(error)


def bulk_add_sequences(request):

    for machine_name in jsonSpiderCommon["machine"]:
        # Submission Group Table
        add_data_sirius_submission_group(machine_name, jsonSpiderCommon)
        # print ("SiriusSubmissionGroup saved")
        current_sirius_submission_group = SiriusSubmissionGroup.objects.using(
            'spider_db').all().order_by("-submission_group_id")[0]

        add_data_database(request, current_sirius_submission_group)

        current_sirius_submission_group.submission_group_status = "Queued"
        current_sirius_submission_group.save(using='spider_db')
    return JsonResponse(json_output(True, "Submission Successful!"), safe=False)


def escape_special_char_folder(strng):
    strng = strng.replace(' ', "_").replace('/', "_").replace("<", "_").replace(">", "_").replace(
        "*", "_").replace("|", "_").replace("*", "_").replace(":", "_").replace('"', "_").replace("?", "_")
    return strng

# @csrf_exempt


def spider_service(request):
    print("spider_service method call")
    if request.method == 'POST':
        print("Post method call")

        get_basic_info(request)
        get_spider_service_data(request)
        get_driver_install_data(request)
        get_gfe_install_data(request)

        if 'btnSelectTemplate' in request.POST:
            return HttpResponseRedirect('/GetData/')
        if 'btnSelectTaskRelease' in request.POST:
            return HttpResponseRedirect('/GetData/Task/')
        if 'Resubmit' in request.POST:
            return HttpResponseRedirect('/GetData/Resubmit/')

    else:
        print("else method call")
        submission_group_id = request.GET.get("submission_group_id")
        sirius_job_config = SiriusSubmissionConfigData.objects.using(
            'spider_db').filter(submission_group_id__iexact=submission_group_id)

        config_data_default = utils.get_default_config_data()
        driver_install_default = utils.get_default_driver_install_data()
        gfe_install_default = utils.get_default_gfe_install_data()

        data_defualt = dict()
        for job_sub in sirius_job_config:
            if job_sub.data_type == 'SpiderService' and job_sub.data_key != "DrvBranch":
                config_data_default[job_sub.data_key] = job_sub.data_value
            if job_sub.data_type == 'DriverInstall':
                driver_install_default[job_sub.data_key] = job_sub.data_value

        sirius_job_submission = SiriusSubmissionGroup.objects.using(
            'spider_db').filter(submission_group_id__iexact=submission_group_id)
        lst_job_submission = list(sirius_job_submission)

        if len(sirius_job_submission) > 0:
            data_defualt["submission_group_name"] = lst_job_submission[0].submission_group_name
            data_defualt["machine"] = lst_job_submission[0].machine

        return render(request, 'GetData/SiriusTest.html', {'DataDefault': data_defualt, 'ConfigDataDefault': config_data_default, 'GFEInstallData': gfe_install_default, 'DriverInstall': driver_install_default})


def validate_groupname(request):
    submission_group_name = request.GET.get('submission_group_name', None)
    data = {
        'is_taken': SiriusSubmissionGroup.objects.using('spider_db').filter(submission_group_name__iexact=submission_group_name).exists()
    }
    return JsonResponse(data)


def rename_groupname(request):
    try:
        submission_group_name = request.GET.get('submission_group_name', None)
        new_submission = request.GET.get('new_submission', None)
        print(submission_group_name, new_submission)
        current_sirius_submission_group = SiriusSubmissionGroup.objects.using(
            'spider_db').filter(submission_group_name__iexact=submission_group_name)[0]
        current_sirius_submission_group.submission_group_name = new_submission
        current_sirius_submission_group.save(using='spider_db')

        data = {
            'is_taken': True
        }
        print(data)
        return JsonResponse(data)
    except Exception as error:
        print(error)
        return False, str(error)

# def update_submission_group_retire(request):
#     try:
#         submission_group_id = request.GET.get('submission_group_id', None)
