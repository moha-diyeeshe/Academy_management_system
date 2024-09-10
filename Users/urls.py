from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('users/<int:user_id>/assign_permissions/', views.user_assign_permissions, name='user_assign_permissions'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.add_group, name='add_group'),
    path('groups/permission/<int:group_id>/edit/', views.assign_group_permission, name='assign_group_permission'),
    path('groups/<int:group_id>/update/', views.update_group, name='update_group'),
    path('users/<int:user_id>/assign-groups/', views.assign_groups_to_user, name='assign_groups_to_user'),
    path('error-logs/', views.error_log_list, name='error_log_list'),
    path('user_change_password/', views.user_change_password, name='user_change_password'),

    path('audit-trials/', views.audit_trial_list, name='audit_trial_list'),
    path('users/<int:user_id>/change-password/', views.admin_change_password, name='admin_change_password'),    
    path('activity-logs/', views.activity_log_list, name='activity_log_list'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

]