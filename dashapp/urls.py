from django.urls import path


from . import views

urlpatterns = [
    path('', views.index, name='index'),  # This is the root URL
    path('assets/', views.asset_list, name='asset_list'),
    path('asset/manage/', views.register_asset, name='register_asset'),
    path('asset/manage/<int:pk>/', views.update_asset, name='update_asset'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teacher/register/', views.register_teacher, name='register_teacher'),
    path('teacher/update/<int:pk>/', views.update_teacher, name='update_teacher'),
    path('courses/', views.course_list, name='course_list'),
    path('course/register/', views.register_course, name='register_course'),
    path('course/update/<int:pk>/', views.update_course, name='update_course'),
    path('classes/', views.class_list, name='class_list'),
    path('class/register/', views.register_class, name='register_class'),
    path('class/update/<int:pk>/', views.update_class, name='update_class'),
    path('students/', views.student_list, name='student_list'),
    path('student/register/', views.register_student, name='register_student'),
    path('student/update/<int:pk>/', views.update_student, name='update_student'),
    path('student/status/<int:student_id>/', views.mark_as_incomplete, name='incomplete'),
    path('student/restart/<int:student_id>/', views.restart_student_status, name='restart_student_status'),
    path('payments/', views.payments_list, name='payments_list'),
    path('payment/receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    path('payments/add/', views.add_payment, name='add_payment'),
    path('payments/update/<int:payment_id>/', views.update_payment, name='update_payment'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/update/<int:expense_id>/', views.update_expense, name='update_expense'),
    path('student-report/', views.student_report, name='student_report'),
    path('teacher-report/', views.teacher_report, name='teacher_report'),
    path('income-statement-report/', views.income_statement_report, name='income_statement_report'),



]


