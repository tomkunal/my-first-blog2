# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from datetime import datetime

class Testtempfoldertree(models.Model):
    projectid = models.IntegerField(db_column='ProjectID', primary_key=True)  # Field name made lowercase.
    parentid = models.IntegerField(db_column='ParentID')
    childid = models.IntegerField(db_column='ChildID')
    displayorder = models.IntegerField(db_column='DisplayOrder')
    
    class Meta:
        managed = False
        db_table = 'Testtempfoldertree'
        unique_together = (('projectid', 'parentid','childid'),)

    def __str__(self):
        return str(self.parentid) + " " + str(self.childid)


class Testtempfolderinfo(models.Model):
    projectid = models.IntegerField(db_column='ProjectID', primary_key=True)  # Field name made lowercase.
    folderid = models.IntegerField(db_column='FolderID')
    foldertitle = models.CharField(db_column='FolderTitle', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ancestoridpath = models.CharField(db_column='AncestorIDPath', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Testtempfolderinfo'
        unique_together = (('projectid', 'folderid'),)

    def __str__(self):
        return str(self.projectid) + " " + str(self.folderid) + " " + self.foldertitle + " "+ self.ancestoridpath 


# class Testtempgeneralinfo(models.Model):
#     projectid = models.IntegerField(db_column='ProjectID', primary_key=True)  # Field name made lowercase.
#     issueid = models.IntegerField(db_column='IssueID')  # Field name made lowercase.
#     displayid = models.CharField(db_column='DisplayID', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     issuetitle = models.CharField(db_column='IssueTitle', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     fieldint10 = models.IntegerField(db_column='FieldInt10', blank=True, null=True)  # Field name made lowercase.
#     fieldvarcharlong12 = models.CharField(db_column='FieldVarcharLong12', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     testtempfolderid = models.IntegerField(db_column='TestTempFolderID', blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'TestTempGeneralInfo'
#         unique_together = (('projectid', 'issueid'),)

#     def __str__(self):
#         return str(self.issueid) + " " + self.issuetitle + " " + self.fieldint10 + " "+ self.fieldvarcharlong12 


#----------------------Sirius-DB---------------------

class SiriusJobTable(models.Model):
    submission_id = models.BigIntegerField(db_column='Submission_Id')  # Field name made lowercase.
    job_id = models.BigAutoField(db_column='Job_Id', primary_key=True)  # Field name made lowercase.
    job_status = models.CharField(db_column='Job_Status', max_length=50, default="Queued", blank=True, null=True)  # Field name made lowercase.
    template_id = models.CharField(db_column='Template_Id', max_length=127, default=0, blank=True, null=True)  # Field name made lowercase.
    sequence = models.CharField(db_column='Sequence', max_length=1020, blank=True, null=True)  # Field name made lowercase.
    root_folder = models.CharField(db_column='Root_Folder', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    file_name = models.CharField(db_column='File_Name', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    bat_analysis_id = models.BigIntegerField(db_column='BAT_Analysis_Id', blank=True, null=True)  # Field name made lowercase.
    job_start_time = models.DateTimeField(db_column='Job_Start_Time', blank=True, null=True)  # Field name made lowercase.
    job_end_time = models.DateTimeField(db_column='Job_End_Time', blank=True, null=True)  # Field name made lowercase.
    job_result = models.CharField(db_column='Job_Result', max_length=50, blank=True, null=True)  # Field name made lowercase.
    job_guid = models.CharField(db_column='Job_Guid', max_length=256, blank=True, null=True)  # Field name made lowercase.
   
    class Meta:
        managed = False
        db_table = 'Sirius_Job_Table'


class SiriusTaskInfo(models.Model):
    job_id = models.BigIntegerField(db_column='Job_Id', primary_key=True)
    task_id = models.BigIntegerField(db_column='Task_Id')
    project_id = models.BigIntegerField(db_column='Project_ID')
    task_create_update_info = models.CharField(db_column='Task_Create_Update_Info', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    last_modified = models.DateTimeField(db_column='Last_Modified', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[Sirius_Task_Info]'


class SiriusSubmission(models.Model):
    submission_group_id = models.BigIntegerField(db_column='Submission_Group_Id')  # Field name made lowercase.
    submission_id = models.BigAutoField(db_column='Submission_Id', primary_key=True)  # Field name made lowercase.
    test_config_file_path = models.CharField(db_column='Test_Config_File_Path', default="\\\\netapp-pu02\\gpu_qa_pu\\public\\White_Box_Testing\\Sirius\\Data\\SpiderTest\\SpiderBasicConfig\\SpiderBasicConfig.conf", max_length=2000, blank=True, null=True)  # Field name made lowercase.
    submission_time = models.DateTimeField(db_column='Submission_Time', default=datetime.now)  # Field name made lowercase.
    submission_started_time = models.DateTimeField(db_column='Submission_Started_Time', blank=True, null=True)  # Field name made lowercase.
    submission_finished_time = models.DateTimeField(db_column='Submission_Finished_Time', blank=True, null=True)  # Field name made lowercase.
    resubmitted = models.BigIntegerField(db_column='Resubmitted', default=0)  # Field name made lowercase.
    submission_status = models.CharField(db_column='Submission_Status', default="Queued", max_length=50)  # Field name made lowercase.
    run_count = models.SmallIntegerField(db_column='Run_Count', default=0, blank=True, null=True)  # Field name made lowercase.
    devtest_update_path = models.CharField(db_column='DevTest_Update_Path', default="none", max_length=510, blank=True, null=True)  # Field name made lowercase.
    submission_notes = models.CharField(db_column='Submission_Notes', max_length=510, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Sirius_Submission'


class SiriusSubmissionConfigData(models.Model):
    submission_group_id = models.BigIntegerField(db_column='Submission_Group_Id')  # Field name made lowercase.
    submission_id = models.BigIntegerField(db_column='Submission_Id')  # Field name made lowercase.
    data_type = models.CharField(db_column='Data_Type', max_length=50)  # Field name made lowercase.
    data_key = models.CharField(db_column='Data_Key', max_length=125)  # Field name made lowercase.
    data_value = models.CharField(db_column='Data_Value', max_length=2000)  # Field name made lowercase.
    config_data_id = models.BigAutoField(db_column='Config_Data_Id', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Sirius_Submission_Config_Data'


class SiriusSubmissionGroup(models.Model):
    submission_group_id = models.BigAutoField(db_column='Submission_Group_Id', primary_key=True)  # Field name made lowercase.
    submission_group_name = models.CharField(db_column='Submission_Group_Name', max_length=50)  # Field name made lowercase.
    submission_group_time = models.DateTimeField(db_column='Submission_Group_Time', default=datetime.now, blank=True, null=True)  # Field name made lowercase.
    submission_owner = models.CharField(db_column='Submission_Owner', max_length=50, blank=True, null=True)  # Field name made lowercase.
    submission_group_status = models.CharField(db_column='Submission_Group_Status', max_length=50, default="Queued", blank=True, null=True)  # Field name made lowercase.
    submission_test_type = models.CharField(db_column='Submission_Test_Type', max_length=50, default="Spider", blank=True, null=True)  # Field name made lowercase.
    priority = models.IntegerField(db_column='Priority', default=5)  # Field name made lowercase.
    machine = models.CharField(db_column='Machine', max_length=50, blank=True, null=True)  # Field name made lowercase.
    machine_pool = models.CharField(db_column='Machine_Pool', max_length=50, blank=True, null=True)  # Field name made lowercase.
    requester = models.CharField(db_column='Requester', max_length=50, blank=True, null=True)  # Field name made lowercase.
    alias = models.CharField(db_column='Alias', max_length=50, blank=True, null=True)  # Field name made lowercase.
    starred = models.IntegerField(db_column='Starred', default=0)  # Field name made lowercase.
    submission_group_notes = models.CharField(db_column='Submission_Group_Notes', max_length=512, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Sirius_Submission_Group'
