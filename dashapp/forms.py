from django import forms
from .models import Asset, Course, Expense, Payment, Student, Teacher,Glass, Transaction

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['asset_name', 'number_of_assets', 'purchase_date', 'purchase_price', 'description']



class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'profile_photo']


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'duration_months', 'price_per_month']



class ClassForm(forms.ModelForm):
    class Meta:
        model = Glass
        fields = ['name', 'course', 'teacher', 'scheduled_time']

    
    def __init__(self, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        # Ensure the querysets are populated (this is typically automatic)
        self.fields['course'].queryset = Course.objects.all()
        self.fields['teacher'].queryset = Teacher.objects.all()







class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'phone', 'address', 'reference_name', 'reference_phone', 'course', 'student_class', 'photo']




class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_type', 'amount_paid', 'discount']

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['payment_type'].widget = forms.Select(attrs={'class': 'form-control'})
        self.fields['amount_paid'].widget = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        self.fields['discount'].widget = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})




# the expenses form 
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_name', 'category', 'amount',  'description']