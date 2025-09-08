from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    # Home and dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Exam creation and management (Examiner)
    path('create-exam/', views.create_exam, name='create_exam'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('exam/<int:exam_id>/upload-questions/', views.upload_questions, name='upload_questions'),
    path('exam/<int:exam_id>/questions/', views.manage_questions, name='manage_questions'),
    path('exam/<int:exam_id>/delete-all-questions/', views.delete_all_questions, name='delete_all_questions'),
    path('exam/<int:exam_id>/publish/', views.publish_exam, name='publish_exam'),
    path('exam/<int:exam_id>/results/', views.exam_results, name='exam_results'),
    path('exam/<int:exam_id>/publish-results/', views.publish_results, name='publish_results'),
    
    # Exam taking (Examinee)
    path('join-exam/', views.join_exam, name='join_exam'),
    path('pending/<str:exam_code>/', views.exam_pending, name='exam_pending'),
    path('exam/<str:exam_code>/', views.take_exam, name='take_exam'),
    path('exam/<str:exam_code>/start/', views.start_exam, name='start_exam'),
    path('exam/<str:exam_code>/submit/', views.submit_exam, name='submit_exam'),
    path('exam/<str:exam_code>/result/', views.view_result, name='view_result'),
    
    # History and results
    path('my-exams/', views.my_exams, name='my_exams'),
    path('exam-history/', views.exam_history, name='exam_history'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
]
