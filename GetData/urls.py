from django.urls import path
from . import views
from django.shortcuts import render 
from django.conf import settings
from django.conf.urls.static import static

app_name ='GetData'

urlpatterns = [
 
    path('LoadTree', views.load_tree),
    path('',views.render_page),
    path('Task/',views.render_task_page),
    path('Game/',views.render_game),
    path('Result/',views.render_result_page),
    path('HomePage/',views.render_start_page),
    path('Grid/',views.render_nested_page),
    path('loadTemplate',views.load_template),
    path('login/',views.login),
    path('GetTask/',views.load_task),
    path('knowFeature',views.know_feature),
    path('time',views.timekunal),
    path('ResubmittedSubmission/', views.get_all_submission_for_submission_group),
    path('ValidateGroupname/', views.validate_groupname, name='validate_groupname'),
    path('RenameGroupname/', views.rename_groupname, name='rename_groupname'),
    path('ResubmittedJobs/', views.get_all_job_for_submission),
    path('Resubmit/',views.render_resubmit_page),
    path('SubmisionName/', views.get_all_submission_name),
    path('BulkUpdate', views.bulk_add_sequences, name='bulk_add_sequences'),
    #path('SiriusJobStatus/', views.sirius_job_status, name='sirius_job_status'),
    path('SpiderService/', views.spider_service, name='spider_service'),
    path('ResultGrid/', views.get_result_table),
  #  path('ResultJobTable/', views.getJobTable),
    path('ResultSubmissionGrid/', views.get_submission_group_table)
     #http://127.0.0.1:8000/GetDataPage/test
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
