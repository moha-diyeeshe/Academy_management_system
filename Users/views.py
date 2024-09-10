from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import ActivityLog, AuditTrials, ErrorLogs, Users,Permission,Group
from .forms import CustomPasswordChangeForm, CustomUserCreationForm, CustomUserUpdateForm, UserProfileForm
from Users.utils import log_activity, log_error
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm


# User Login View
def user_login(request):
    """
    Handles user login, authenticates using email and password.
    If user_must_change_password is True, redirects to change password page.
    """
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                # Check if the user must change their password
                if user.user_must_change_password:
                    login(request, user)
                    log_activity(request, 'logged in but must change password', 'user', user.id)
                    messages.warning(request, 'You must change your password before proceeding.')
                    return redirect('user_change_password')  # Redirect to password change page
                else:
                    login(request, user)
                    log_activity(request, 'logged in', 'user', user.id)
                    messages.success(request, 'Login successful.')
                    return redirect('index')  # Redirect to your main page after successful login
            else:
                messages.error(request, 'Invalid email or password.')
                log_error(request, 'Failed login attempt')

        return render(request, 'login.html')

    except Exception as e:
        log_error(request, e)
        messages.error(request, 'An unexpected error occurred. Please try again.')
        return render(request, 'login.html')





# User Logout View
@login_required
def user_logout(request):
    """
    Handles user logout and logs the activity.
    """
    log_activity(request, 'logged out', 'user', request.user.id)
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


# List Users View with Search and Pagination
@login_required
@permission_required('Users.view_users', raise_exception=True)
def user_list(request):
    """
    Displays a list of users with search and pagination.
    """
    try:
        search_query = request.GET.get('q', '')
        users = Users.objects.all()

        # If search query exists, filter users
        if search_query:
            users = users.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # Pagination
        paginator = Paginator(users, 10)  # Show 10 users per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

         # Debugging: Ensure the queryset is correct
        print(f"Queryset returned: {users.count()} students")
        context = {
            'users': users,
            'page_obj': page_obj,
            'search_query': search_query,
        }

        return render(request, 'users/user_list.html', context)

    except Exception as e:
        # Log any errors
        log_error(request, e)
        # Display an error message and return an empty user list
        messages.error(request, "An error occurred while fetching the user list.")
        return render(request, 'users/user_list.html', {
            'users': None,
            'page_obj': None,
            'search_query': search_query,
        })



# Add a New User View
@login_required
@permission_required('Users.add_user', raise_exception=True)
def add_user(request):
    """
    Handles the creation of a new user with default password.
    """
    try:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST, request.FILES)
            if form.is_valid():
                user = form.save(commit=False)
                username = user.username
                password = 'Harsan123'  # The generated password

                user.save()
                log_activity(request, 'added user', 'user', user.id)
                messages.success(request, f"User created successfully. Username: {username}, Password: {password}")
                return redirect('user_list')  # Redirect to user list page after adding
            else:
                print(form.errors)
        else:
            form = CustomUserCreationForm()

        return render(request, 'users/add_user.html', {'form': form})
    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while adding the user.")
        return render(request, 'users/add_user.html', {'form': form})


# Update an Existing User View
@login_required
@permission_required('Users.change_user', raise_exception=True)
def update_user(request, user_id):
    """
    Handles updating an existing user.
    """
    try:
        user = get_object_or_404(Users, pk=user_id)

        if request.method == 'POST':
            form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                log_activity(request, 'updated user', 'user', user.id)
                messages.success(request, f"User {user.get_full_name()} updated successfully.")
                return redirect('user_list')  # Redirect to user list after update
            else:
                print(form.errors)
        else:
            form = CustomUserUpdateForm(instance=user)

        return render(request, 'users/update_user.html', {'form': form})
    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while updating the user.")
        return render(request, 'users/update_user.html', {'form': form, 'user': user})









# Assign Permissions to a User
@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_assign_permissions(request, user_id):
    user = get_object_or_404(Users, pk=user_id)
    permissions = Permission.objects.all()

    if user.is_superuser:
        messages.error(request, "You cannot edit permissions for a superuser.")
        return redirect('user_list')

    try:
        if request.method == 'POST':
            selected_permissions = request.POST.getlist('permissions')
            user.user_permissions.clear()  # Clear all current permissions

            # Assign the selected permissions
            for perm_id in selected_permissions:
                perm = Permission.objects.get(id=perm_id)
                user.user_permissions.add(perm)

            log_activity(request, f'Updated permissions for user {user.get_full_name()}', 'user', user.id)
            messages.success(request, 'Permissions updated successfully.')
            return redirect('user_list')
        context = {
        'user': user,
        'permissions': permissions,
        'user_permissions': user.user_permissions.all()
         }

        return render(request, 'users/user_permissions.html', context)
    except Exception as e:
        log_error(request, e)
        messages.error(request, 'An error occurred while assigning permissions.')
        return render(request, 'users/user_permissions.html', {'user': user, 'permissions': permissions, 'user_permissions': user.user_permissions.all()})

    




# users assign for groups 
@login_required
@permission_required('auth.change_user', raise_exception=True)
def assign_groups_to_user(request, user_id):
    try:
        user = get_object_or_404(Users, id=user_id)

        if user.is_superuser:
            messages.error(request, "You cannot assign groups to a superuser.")
            return redirect('user_list')

        if request.method == 'POST':
            group_ids = request.POST.getlist('groups')  # Get selected group IDs from POST data
            groups = Group.objects.filter(id__in=group_ids)
            user.groups.set(groups)  # Update the user's group memberships
            
            # Log the activity of assigning groups to the user
            log_activity(request, f"Assigned groups to {user.get_full_name()}", 'auth_group', user.id)
            
            messages.success(request, f"Groups updated successfully for {user.get_full_name()}.")
            return redirect('user_list')  # Redirect back to user list or wherever you want

        # Fetch all available groups and the groups the user currently belongs to
        all_groups = Group.objects.all()
        user_groups = user.groups.all()
        context = {
        'user': user,
        'all_groups': all_groups,
        'user_groups': user_groups,
    }
        return render(request, 'users/assign_groups.html', context)

    except Exception as e:
        log_error(request, e)
        messages.error(request, "An error occurred while assigning groups.")

        context = {
            'user': user,
            'all_groups': all_groups,
            'user_groups': user_groups,
        }
        return render(request, 'users/assign_groups.html', context)



# Group Management
@login_required
@permission_required('auth.view_group', raise_exception=True)
def group_list(request):
    try:
        search_query = request.GET.get('q', '')
        if search_query:
            groups = Group.objects.filter(name__icontains=search_query)
        else:
            groups = Group.objects.all()

        paginator = Paginator(groups, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
         # Debugging: Ensure the queryset is correct
        print(f"Queryset returned: {groups.count()} students")
        return render(request, 'groups/group_list.html', {'search_query': search_query, 'page_obj': page_obj})
    



    except Exception as e:
        log_error(request, e)
        messages.error(request, 'An error occurred while fetching groups.')
        return render(request, 'groups/group_list.html', {'search_query': search_query, 'page_obj': page_obj})
   


@login_required
@permission_required('auth.add_group', raise_exception=True)
def add_group(request):
    try:
        if request.method == 'POST':
            group_name = request.POST.get('group_name')
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                messages.success(request, f'Group "{group_name}" created successfully.')
                log_activity(request, f'Added new group {group_name}', 'group', group.id)
            else:
                messages.info(request, f'Group "{group_name}" already exists.')
            return redirect('group_list')
    except Exception as e:
        log_error(request, e, )
        messages.error(request, 'An error occurred while adding the group.')

    return render(request, 'groups/add_group.html')


@login_required
@permission_required('auth.change_group', raise_exception=True)
def update_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    try:
        if request.method == 'POST':
            group_name = request.POST.get('group_name')
            if Group.objects.filter(name=group_name).exclude(id=group.id).exists():
                messages.error(request, f'The group name "{group_name}" already exists. Please choose a different name.')
            else:
                group.name = group_name
                group.save()
                log_activity(request, f'Updated group {group_name}', 'group', group.id)
                messages.success(request, f'Group "{group_name}" updated successfully.')
                return redirect('group_list')
    except Exception as e:
        log_error(request, e)
        messages.error(request, 'An error occurred while updating the group.')

    return render(request, 'groups/update_group.html', {'group': group})


@login_required
@permission_required('auth.change_group', raise_exception=True)
def assign_group_permission(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    try:
        if request.method == 'POST':
            permissions = request.POST.getlist('permissions')
            group.permissions.clear()
            group.permissions.add(*permissions)
            log_activity(request, f'Updated permissions for group {group.name}', 'group', group.id)
            messages.success(request, f'Permissions updated for "{group.name}".')
            return redirect('group_list')
    except Exception as e:
        log_error(request, e)
        messages.error(request, 'An error occurred while assigning permissions.')

    permissions = Permission.objects.all()
    group_permissions = group.permissions.all()

    return render(request, 'groups/edit_group.html', {
        'group': group,
        'permissions': permissions,
        'group_permissions': group_permissions,
    })


# Error Log Views
@login_required
@permission_required('Users.view_errorlogs', raise_exception=True)
def error_log_list(request):
    try:
        error_logs = ErrorLogs.objects.all().order_by('-date_recorded')
        paginator = Paginator(error_logs, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'logs/error_log_list.html', {'page_obj': page_obj})
    except Exception as e:
        log_error(request, e)
        messages.error(request, 'An error occurred while fetching the error logs.')
        return render(request, 'logs/error_log_list.html', {'page_obj': page_obj})





# Audit Trials Log Views
@login_required
@permission_required('Users.view_audittrials', raise_exception=True)
def audit_trial_list(request):
    try:
        audit_trials = AuditTrials.objects.all().order_by('-date_of_action')
        paginator = Paginator(audit_trials, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'logs/audit_trials_list.html', {'page_obj': page_obj})
    except Exception as e:
        log_error(request, e)
        messages.error(request, 'An error occurred while fetching the audit trials.')
        return render(request, 'logs/audit_trials_list.html', {'page_obj': page_obj})





# Activity Log Views
@login_required
@permission_required('Users.view_activitylog', raise_exception=True)
def activity_log_list(request):
    try:
        activity_logs = ActivityLog.objects.all().order_by('-timestamp')
        paginator = Paginator(activity_logs, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        log_activity(request, 'Viewed activity logs list', 'activitylog', None)
    except Exception as e:
        log_error(request,e)
        messages.error(request, 'An error occurred while fetching the activity logs.')

    return render(request, 'logs/activity_log_list.html', {'page_obj': page_obj})



@login_required
def user_change_password(request):
    """
    View for changing the user's password. Handles both user-initiated and forced password changes.
    Logs activity and handles exceptions with proper logging.
    """
    must_change_password = request.user.user_must_change_password  # Check if the user must change password

    try:
        # Handle form submission (POST request)
        if request.method == 'POST':
            form = CustomPasswordChangeForm(user=request.user, data=request.POST, must_change_password=must_change_password)
            if form.is_valid():
                user = form.save(commit=False)
                update_session_auth_hash(request, user)  # Prevent session invalidation
                user.user_must_change_password = False  # Reset the flag after password change
                user.save()

                # Log the successful password change
                log_activity(request, 'changed password', 'user', request.user.id)

                messages.success(request, 'Your password has been successfully changed.')
                return redirect('index')  # Redirect to the dashboard or another page
            else:
                messages.error(request, 'Please correct the error(s) below.')
        else:
            # Render the form (GET request)
            form = CustomPasswordChangeForm(user=request.user, must_change_password=must_change_password)

        return render(request, 'users/change_password.html', {
            'form': form,
            'must_change_password': must_change_password
        })

    except Exception as e:
        # Log the error and display an error message
        log_error(request, e)  # Assuming this logs exceptions properly
        messages.error(request, 'An error occurred while changing the password. Please try again later.')
        return render(request, 'user_change_password.html', {
            'form': form,
            'must_change_password': must_change_password
        })



@login_required
@permission_required('Users.change_user', raise_exception=True)
def admin_change_password(request, user_id):
    """
    Allows the admin to change the user's password and force the user to change it upon next login.
    """
    user = get_object_or_404(Users, pk=user_id)
    
    try:
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.user_must_change_password = True  # Set user_must_change_password to True
                user.save()
                log_activity(request, f'Admin changed password for {user.username}', 'user', user.id)
                messages.success(request, f"Password changed successfully for {user.get_full_name()}. The user must change their password upon next login.")
                return redirect('user_list')
            else:
                messages.error(request, "There was an error changing the password. Please try again.")
                print(form.errors)
        else:
            form = SetPasswordForm(user)
        
        return render(request, 'users/change_password.html', {
            'form': form,
            'user': user
        })

    except Exception as e:
        log_error(request, e)
        messages.error(request, "An error occurred while changing the password.")
        return redirect('user_list')
    




@login_required
def profile_view(request):
    """
    Displays the user's profile.
    """
    user = request.user
    return render(request, 'users/profile.html', {'user': user})

@login_required
def edit_profile_view(request):
    """
    Allows the user to edit their profile.
    """
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'users/edit_profile.html', {'form': form, 'user': user})