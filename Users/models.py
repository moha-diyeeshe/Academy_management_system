from django.contrib.auth.models import AbstractUser, Group,Permission
from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.utils import timezone

# Create your models here.


class Users(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.CharField(max_length=15, blank=False, null=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    modified_at = models.DateTimeField(auto_now=True)
    user_must_change_password = models.BooleanField(default=False)
    title = models.CharField(max_length=50, blank=True, null=True)
    login_attempts = models.IntegerField(default=0, blank=True, null=True)
    last_login_device = models.TextField(blank=True, null=True)



     # Add related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions_set', blank=True)

    USERNAME_FIELD = 'email'  # Use email to login instead of username
    REQUIRED_FIELDS = ['username']  # Keep username required for Django Admin compatibility

    class Meta:
        db_table = 'users'
        ordering = ['-username']

        permissions = [
            ('manage_role_groups', 'Can Add Or Delete Role From The Group'),
            ('remove_role_from_group', 'Can Remove Role From Group'),
            ('assign_user_to_group', 'Can Assign User To Group'),
            ('role_report', 'Can See Roles Report'),
            ('view_dashboard', 'Can view dashboard'),
        ]


    def save(self, *args, **kwargs):
        # Generate a username if it's not provided
        if not self.username:
            self.username = self.generate_username()

        # Set default password as 'Harsan123' if not provided
        if not self.password:
            self.password = self.generate_password()

        # Call the parent save method
        super().save(*args, **kwargs)

    def generate_username(self):
        # Generate a username from the first name and last name or fallback to email
        base_username = slugify(f"{self.first_name}") or slugify(self.email.split('@')[0])
        username = base_username

        # Ensure the username is unique
        num = 1
        while Users.objects.filter(username=username).exists():
            username = f"{base_username}{num}"
            num += 1

        return username

    def generate_password(self):
        # Set the default password to 'Harsan123'
        default_password = 'Harsan123'
        
        # Hash the password before saving
        return self.set_password(default_password)

    def __str__(self):
        return self.email

    def profile_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images.jpg'  # Default avatar if none is uploaded

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    




class ErrorLogs(models.Model):
    Username = models.CharField(max_length=20, db_index=True)
    Name = models.CharField(max_length=500, db_index=True)
    Expected_error = models.CharField(max_length=500, db_index=True)
    field_error = models.CharField(max_length=500, db_index=True)
    trace_back = models.TextField(max_length=500)
    line_number = models.IntegerField(db_index=True)
    date_recorded = models.DateTimeField(auto_now_add=True, db_index=True)
    browser = models.CharField(max_length=500, db_index=True)
    ip_address = models.CharField(max_length=500, db_index=True)
    user_agent = models.TextField(max_length=500)
    Avatar = models.FileField(upload_to="errorlogs/", null=True, blank=True)

    class Meta:
        db_table = 'errorlogs'
        ordering = ['-date_recorded']




class AuditTrials(models.Model):
    Avatar = models.FileField(upload_to="trials/")
    Username = models.CharField(max_length=20)
    path = models.CharField(max_length=60, null=True, blank=True)
    Name = models.CharField(max_length=200)
    Actions = models.CharField(max_length=400)
    Module = models.CharField(max_length=400)
    date_of_action = models.DateTimeField(auto_now_add=True)
    operating_system = models.CharField(max_length=200)
    browser = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=200)
    user_agent = models.TextField(max_length=200)

    class Meta:
        db_table = 'audittrials'

    def reduceActions(self):
        return f"{self.Actions[:30]}..." if len(self.Actions) > 30 else self.Actions









class ActivityLog(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    content_type = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)
    # ip_address = models.CharField(max_length=255)
    # os = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"