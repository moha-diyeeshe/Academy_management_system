from django.db import models
from django.utils import timezone



# Create your models here.

class Asset(models.Model):
    asset_name = models.CharField(max_length=255)
    number_of_assets = models.IntegerField()
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset_name} purchased on {self.purchase_date}"

    


class Teacher(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    profile_photo = models.ImageField(upload_to='teacher_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration_months = models.IntegerField()
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name





class Glass(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.course.name}"

    


# students moodel that have an id start 1000
class Student(models.Model):
    STATUS_CHOICES = [
        ('Incomplete', 'Incomplete'),
        ('Active', 'Active'),
        ('Graduate', 'Graduate'),
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    reference_name = models.CharField(max_length=255)
    reference_phone = models.CharField(max_length=15)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    student_class = models.ForeignKey(Glass, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    student_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def update_status(self):
        """Update the student's status based on the payments and course progress."""
        transactions = self.transaction_set.all()
        total_paid = sum(transaction.amount_paid for transaction in transactions)
        required_amount = sum(transaction.required_amount for transaction in transactions)

        if total_paid >= required_amount:
            if timezone.now() >= self.course.end_date:  # Assuming course has an end_date field
                self.status = 'Graduate'
            else:
                self.status = 'Active'
        else:
            self.status = 'Incomplete'

        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.student_id})"
    






class Transaction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    student_class = models.ForeignKey(Glass, on_delete=models.CASCADE)
    date_paid = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_paid(self):
        """Calculate the total amount paid by the student for this class."""
        return sum(payment.amount_paid for payment in Payment.objects.filter(transaction=self))

    @property
    def required_amount(self):
        """Calculate the required amount based on the class's course price and duration."""
        course_duration = self.student_class.course.duration_months
        return max(self.student_class.course.price_per_month * course_duration, 0)

    def save(self, *args, **kwargs):
        """Update the student's status based on total payments made for the class."""
        super().save(*args, **kwargs)
        if self.total_paid >= self.required_amount:
            self.student.status = 'Graduate'
        else:
            self.student.status = 'Active'
        self.student.save()

    def __str__(self):
        return f"Transaction for {self.student.first_name} {self.student.last_name} in {self.student_class.name}"



class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('registration', 'Registration Fee'),
        ('monthly', 'Monthly Fee'),
        ('certificate', 'Certificate Fee'),
    ]

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Discount applied per payment
    reference_number = models.PositiveIntegerField(unique=True, editable=False)  # Unique reference number per payment
    date_paid = models.DateField(auto_now_add=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            last_payment = Payment.objects.all().order_by('reference_number').last()
            if last_payment:
                self.reference_number = last_payment.reference_number + 1
            else:
                self.reference_number = 1000  # Starting point for reference numbers
        super().save(*args, **kwargs)
        self.update_transaction_status()

    def update_transaction_status(self):
        """Update the transaction status based on payments made."""
        transaction = self.transaction
        transaction.save()

    def __str__(self):
        return f"Payment of {self.amount_paid} ({self.payment_type}) for Transaction {self.transaction.reference_number}"


# the expenses model 
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('salary', 'Salary'),
        ('supplies', 'Supplies'),
        ('maintenance', 'Maintenance'),
        ('utility', 'Utility'),
        ('miscellaneous', 'Miscellaneous'),
    ]
    expense_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_incurred = models.DateField(default=timezone.now)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.expense_name} - {self.amount} on {self.date_incurred}"





