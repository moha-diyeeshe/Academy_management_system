from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import PasswordChangeForm

from .models import Users

class CustomUserCreationForm(forms.ModelForm):
    is_superuser = forms.BooleanField(label="Superuser Status", required=False)

    class Meta:
        model = Users
        fields = ['email', 'phone', 'first_name', 'last_name', 'gender', 'avatar', 'is_admin', 'is_superuser']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password('Harsan123')  # Set the default password here

        user.is_superuser = self.cleaned_data['is_superuser']
        user.is_staff = self.cleaned_data['is_superuser']  # Superuser usually needs staff status

        if commit:
            user.save()
        return user






class CustomUserUpdateForm(forms.ModelForm):
    is_superuser = forms.BooleanField(label="Superuser Status", required=False)

    class Meta:
        model = Users
        fields = ['email', 'phone', 'first_name', 'last_name', 'gender', 'avatar', 'is_admin', 'is_superuser', 'title']




class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        must_change_password = kwargs.pop('must_change_password', False)  # Capture the flag
        super().__init__(*args, **kwargs)

        if must_change_password:
            # Remove the old password field if user is forced to change the password
            self.fields.pop('old_password')

        # Apply Bootstrap styling to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })







class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['avatar', 'first_name', 'last_name', 'phone',  'gender', 'title']
        
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }