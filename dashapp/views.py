from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from Users.models import ActivityLog, Users
from Users.utils import log_activity, log_error
from dashapp.forms import AssetForm, ClassForm, CourseForm, ExpenseForm, PaymentForm, StudentForm, TeacherForm
from dashapp.models import Asset, Course, Expense, Glass, Payment, Student, Teacher, Transaction

from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required

from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

from django.utils.dateparse import parse_date


# Create your views here.




def index(request):
    # Total active students
    total_active_students = Student.objects.filter(status='Active').count()

    # Total revenue and expenses for the current month
    current_month = timezone.now().month
    current_year = timezone.now().year
    total_revenue = Payment.objects.filter(date_paid__year=current_year, date_paid__month=current_month).aggregate(total=Sum('amount_paid'))['total'] or 0
    total_expenses = Expense.objects.filter(date_incurred__year=current_year, date_incurred__month=current_month).aggregate(total=Sum('amount'))['total'] or 0

    # Monthly revenue and expenses for the bar chart
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    monthly_revenue = []
    monthly_expenses = []
    for month in range(1, 13):
        monthly_rev = Payment.objects.filter(date_paid__year=current_year, date_paid__month=month).aggregate(total=Sum('amount_paid'))['total'] or 0
        monthly_exp = Expense.objects.filter(date_incurred__year=current_year, date_incurred__month=month).aggregate(total=Sum('amount'))['total'] or 0
        monthly_revenue.append(monthly_rev)
        monthly_expenses.append(monthly_exp)



    print("Months:", months)
    print("Monthly Revenue:", monthly_revenue)
    print("Monthly Expenses:", monthly_expenses)

    # Last 5 activity logs
    recent_activity_logs = ActivityLog.objects.all().order_by('-timestamp')[:5]

    context = {
        'total_active_students': total_active_students,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'months': months,
        'monthly_revenue': monthly_revenue,
        'monthly_expenses': monthly_expenses,
        'recent_activity_logs': recent_activity_logs,
    }

    return render(request, 'index.html', context)









@login_required
@permission_required('dashapp.view_asset', raise_exception=True)
def asset_list(request):
    try:
        search_query = request.GET.get('q', '')  # Get the search query if present
        if search_query:
            assets = Asset.objects.filter(asset_name__icontains=search_query)
        else:
            assets = Asset.objects.all().order_by('-created_at')

        paginator = Paginator(assets, 10)  # Show 10 assets per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Log user activity
        log_activity(request, action="Viewed Asset List", content_type="Asset", object_id=None)
        
        return render(request, 'assets/assets_list.html', {
            'page_obj': page_obj,
            'search_query': search_query,
        })
    except Exception as e:
        log_error(request, e)
        return render(request, 'assets/assets_list.html', {
            'page_obj': page_obj,
            'search_query': search_query,
        })

# Asset registration
@login_required
@permission_required('dashapp.add_asset', raise_exception=True)
def register_asset(request):
    try:
        if request.method == 'POST':
            form = AssetForm(request.POST)
            if form.is_valid():
                asset = form.save()
                # Log user activity
                log_activity(request, action="Registered Asset", content_type="Asset", object_id=asset.pk)
                return redirect('asset_list')  # Redirect to the asset list after successful registration
        else:
            form = AssetForm()

        return render(request, 'assets/register_asset.html', {'form': form})
    except Exception as e:
        log_error(request, e)
        return render(request, 'error.html', {"message": "Error during asset registration."})

# Asset update
@login_required
@permission_required('dashapp.change_asset', raise_exception=True)
def update_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    try:
        if request.method == 'POST':
            form = AssetForm(request.POST, instance=asset)
            if form.is_valid():
                form.save()
                # Log user activity
                log_activity(request, action="Updated Asset", content_type="Asset", object_id=asset.pk)
                return redirect('asset_list')  # Redirect to the asset list after successful update
            else:
                print(form.errors)
        else:
            form = AssetForm(instance=asset)

        return render(request, 'assets/update_asset.html', {'form': form, 'asset': asset})
    except Exception as e:
        log_error(request, e)
        return render(request, 'assets/update_asset.html', {'form': form, 'asset': asset})



# teachers management page 

# Teacher list view
@login_required
@permission_required('dashapp.view_teacher', raise_exception=True)
def teacher_list(request):
    try:
        search_query = request.GET.get('q', '')  # Get the search query if present
        if search_query:
            teachers = Teacher.objects.filter(
                first_name__icontains=search_query
            ) | Teacher.objects.filter(
                last_name__icontains=search_query
            ) | Teacher.objects.filter(
                phone_number__icontains=search_query
            ).order_by('-created_at')
        else:
            teachers = Teacher.objects.all().order_by('created_at')

        paginator = Paginator(teachers, 10)  # Show 10 teachers per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Log user activity
        log_activity(request, action="Viewed Teacher List", content_type="Teacher", object_id=None)
        return render(request, 'teachers/teacher_list.html', {
            'page_obj': page_obj,
            'search_query': search_query,
        })

        
    except Exception as e:
        log_error(request, e)
        return render(request, 'teachers/teacher_list.html', {
            'page_obj': page_obj,
            'search_query': search_query,
        }) 

# Teacher registration
@login_required
@permission_required('dashapp.add_teacher', raise_exception=True)
def register_teacher(request):
    try:
        if request.method == 'POST':
            form = TeacherForm(request.POST, request.FILES)
            if form.is_valid():
                teacher = form.save()
                # Log user activity
                log_activity(request, action="Registered Teacher", content_type="Teacher", object_id=teacher.pk)
                return redirect('teacher_list')
            else:
                print(form.errors)
        else:
            form = TeacherForm()

        return render(request, 'teachers/register_teacher.html', {'form': form})
    except Exception as e:
        log_error(request, e)
        return render(request, 'teachers/register_teacher.html', {'form': form})

# Teacher update
@login_required
@permission_required('dashapp.change_teacher', raise_exception=True)
def update_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    try:
        if request.method == 'POST':
            form = TeacherForm(request.POST, request.FILES, instance=teacher)
            if form.is_valid():
                form.save()
                # Log user activity
                log_activity(request, action="Updated Teacher", content_type="Teacher", object_id=teacher.pk)
                return redirect('teacher_list')
        else:
            form = TeacherForm(instance=teacher)
        return render(request, 'teachers/update_teacher.html', {'form': form, 'teacher': teacher})
    except Exception as e:
        log_error(request, e)
        return render(request, 'teachers/update_teacher.html', {'form': form, 'teacher': teacher})




# the courses management function
@login_required
@permission_required('dashapp.view_course', raise_exception=True)
def course_list(request):
    try:
        search_query = request.GET.get('q', '')  # Get the search query if present
        if search_query:
            courses = Course.objects.filter(
                name__icontains=search_query
            ) | Course.objects.filter(
                description__icontains=search_query
            ).order_by('-created_at')
        else:
            courses = Course.objects.all().order_by('-created_at')

        paginator = Paginator(courses, 10)  # Show 10 courses per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

      



        return render(request, 'courses/course_list.html', {
            'page_obj': page_obj,
            'search_query': search_query,
        })

    except Exception as e:
        log_error(request, e)
        messages.error(request, "An error occurred while loading the courses.")
        return render(request, 'courses/course_list.html', {
            'page_obj': None,
            'search_query': search_query,
        })







# the regestraion of courses 
@login_required
@permission_required('dashapp.add_course', raise_exception=True)
def register_course(request):
    try:
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save()
                log_activity(request, 'registered course', 'course', course.id, f'User registered the course {course.name}')
                messages.success(request, 'Course registered successfully!')
                return redirect('course_list')
        else:
            form = CourseForm()

        return render(request, 'courses/register_course.html', {'form': form})

    except Exception as e:
        log_error(request, e)
        messages.error(request, "An error occurred while registering the course.")
        return render(request, 'courses/register_course.html', {'form': form})





# the update function of the courses 
@login_required
@permission_required('dashapp.change_course', raise_exception=True)
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    try:
        if request.method == 'POST':
            form = CourseForm(request.POST, instance=course)
            if form.is_valid():
                form.save()
                log_activity(request, 'updated course', 'course', course.id, f'User updated the course {course.name}')
                messages.success(request, 'Course updated successfully!')
                return redirect('course_list')
        else:
            form = CourseForm(instance=course)

        return render(request, 'courses/update_course.html', {'form': form, 'course': course})

    except Exception as e:
        log_error(request, e)
        messages.error(request, "An error occurred while updating the course.")
        return render(request, 'courses/update_course.html', {'form': form, 'course': course})



# the course management page 
@login_required
@permission_required('dashapp.view_glass', raise_exception=True)
def class_list(request):
    try:
        search_query = request.GET.get('q', '')  # Get the search query if present
        if search_query:
            classes = Glass.objects.filter(
                name__icontains=search_query
            ) | Glass.objects.filter(
                course__name__icontains=search_query
            ) | Glass.objects.filter(
                teacher__first_name__icontains=search_query
            ) | Glass.objects.filter(
                teacher__last_name__icontains=search_query
            ).order_by('-created_at')
        else:
            classes = Glass.objects.all().order_by('-created_at')

        paginator = Paginator(classes, 10)  # Show 10 classes per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

         





        return render(request, 'classes/class_list.html', {
            'page_obj': page_obj,
            'search_query': search_query,
        })

    except Exception as e:
        log_error(request, e)
        messages.error(request, "An error occurred while loading the classes.")
        return render(request, 'classes/class_list.html', {
            'page_obj': None,
            'search_query': search_query,
        })





# the regestration function of the classes
@login_required
@permission_required('dashapp.add_glass', raise_exception=True)
def register_class(request):
    try:
        if request.method == 'POST':
            form = ClassForm(request.POST)
            if form.is_valid():
                class_instance = form.save()
                log_activity(request, 'registered class', 'glass', class_instance.id, f'User registered the class {class_instance.name}')
                messages.success(request, 'Class registered successfully!')
                return redirect('class_list')
        else:
            form = ClassForm()

        return render(request, 'classes/register_class.html', {'form': form})

    except Exception as e:
        log_error(request, e)
        messages.error(request, "An error occurred while registering the class.")
        return render(request, 'classes/register_class.html', {'form': form})






# the update function of the classes
@login_required
@permission_required('dashapp.change_glass', raise_exception=True)
def update_class(request, pk):
    class_instance = get_object_or_404(Glass, pk=pk)
    
    try:
        if request.method == 'POST':
            form = ClassForm(request.POST, instance=class_instance)
            if form.is_valid():
                form.save()
                log_activity(request, 'updated class', 'glass', class_instance.id, f'User updated the class {class_instance.name}')
                messages.success(request, 'Class updated successfully!')
                return redirect('class_list')
        else:
            form = ClassForm(instance=class_instance)

        return render(request, 'classes/update_class.html', {'form': form, 'class_instance': class_instance})

    except Exception as e:
        log_error(request, e)
        messages.error(request, "An error occurred while updating the class.")
        return render(request, 'classes/update_class.html', {'form': form, 'class_instance': class_instance})








# List all students with pagination and search functionality
@login_required
@permission_required('dashapp.view_student', raise_exception=True)
def student_list(request):
    """
    View for listing students with search functionality and pagination.
    """
    try:
        search_query = request.GET.get('q', '')  # Get the search query if present
        if search_query:
            students = Student.objects.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(phone__icontains=search_query)
            ).order_by('-created_at')
        else:
            students = Student.objects.all().order_by('-created_at')

        paginator = Paginator(students, 10)  # Show 10 students per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

       

        # Pass the context to the template
        return render(request, 'students/student_list.html', {
            'page_obj': page_obj,
            'search_query': search_query,
        })

    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while loading students.")
        return render(request, 'students/student_list.html', {
            'page_obj': None,
            'search_query': search_query,
        })

# Register a new student
@login_required
@permission_required('dashapp.add_student', raise_exception=True)
def register_student(request):
    """
    View for registering a new student.
    """
    try:
        if request.method == 'POST':
            form = StudentForm(request.POST, request.FILES)
            if form.is_valid():
                student = form.save()
                log_activity(request, 'registered student', 'student', student.student_id)  # Log the activity
                messages.success(request, 'Student registered successfully!')
                return redirect('student_list')
        else:
            form = StudentForm()

        return render(request, 'students/register_student.html', {'form': form})

    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while registering the student.")
        return render(request, 'students/register_student.html', {'form': form})


# Update an existing student's details
@login_required
@permission_required('dashapp.change_student', raise_exception=True)
def update_student(request, pk):
    """
    View for updating an existing student.
    """
    student = get_object_or_404(Student, pk=pk)
    
    try:
        if request.method == 'POST':
            form = StudentForm(request.POST, request.FILES, instance=student)
            if form.is_valid():
                form.save()
                log_activity(request, 'updated student', 'student', student.student_id)  # Log the activity
                messages.success(request, 'Student updated successfully!')
                return redirect('student_list')
        else:
            form = StudentForm(instance=student)

        return render(request, 'students/update_student.html', {'form': form, 'student': student})

    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while updating the student.")
        return render(request, 'students/update_student.html', {'form': form, 'student': student})


# Mark a student's status as incomplete
@login_required
@permission_required('dashapp.change_student', raise_exception=True)
def mark_as_incomplete(request, student_id):
    """
    View to mark a student's status as 'Incomplete'.
    """
    try:
        student = get_object_or_404(Student, pk=student_id)
        student.status = 'Incomplete'
        student.save()
        log_activity(request, 'marked student as incomplete', 'student', student.student_id)  # Log the activity
        messages.success(request, 'Student marked as Incomplete.')
        return redirect('student_list')

    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while marking the student as incomplete.")
        return redirect('student_list')


# Restart a student's status to active
@login_required
@permission_required('dashapp.change_student', raise_exception=True)
def restart_student_status(request, student_id):
    """
    View to restart a student's status to 'Active' if it was 'Incomplete'.
    """
    try:
        student = get_object_or_404(Student, pk=student_id)
        if student.status == 'Incomplete':
            student.status = 'Active'
            student.save()
            log_activity(request, 'restarted student status to active', 'student', student.student_id)  # Log the activity
            messages.success(request, 'Student status restarted to Active.')
        return redirect('student_list')

    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while restarting the student's status.")
        return redirect('student_list')




# View for displaying a specific payment receipt
@login_required
@permission_required('dashapp.view_payment', raise_exception=True)
def payment_receipt(request, payment_id):
    """
    View to display a payment receipt based on the payment ID.
    """
    try:
        # Get the payment object by its ID
        payment = get_object_or_404(Payment, pk=payment_id)

        # Determine the status of the payment (Paid, Partial, Incomplete)
        if payment.amount_paid >= payment.transaction.required_amount:
            status = 'Paid'
        elif payment.amount_paid > 0:
            status = 'Partial'
        else:
            status = 'Incomplete'

        # Log the activity
        log_activity(request, 'viewed payment receipt', 'payment', payment.id)

        # Context to be passed to the template
        context = {
            'payment': payment,
            'status': status,
        }

        return render(request, 'invoices/invoice.html', context)
    
    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while loading the payment receipt.")
        return redirect('payments_list')


# View for listing payments with search and pagination
@login_required
@permission_required('dashapp.view_payment', raise_exception=True)
def payments_list(request):
    """
    View to list payments with search functionality and pagination.
    """
    try:
        # Get the search query from the request
        search_query = request.GET.get('q', '')

        # Start with all payments
        payments = Payment.objects.select_related('transaction__student', 'transaction__student_class__course').order_by('-created_at')

        # Apply search filters if search_query exists
        if search_query:
            payments = payments.filter(
                Q(transaction__student__first_name__icontains=search_query) |
                Q(transaction__student__last_name__icontains=search_query) |
                Q(transaction__student_class__course__name__icontains=search_query) |
                Q(payment_type__icontains=search_query)
            ).order_by('-created_at')

        # Paginate the payments, show 10 payments per page
        paginator = Paginator(payments, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

 



        context = {
            'page_obj': page_obj,
            'search_query': search_query,
        }

        return render(request, 'invoices/payment_list.html', context)

    except Exception as e:
        # Log any errors
        log_error(request, e)
        messages.error(request, "An error occurred while loading the payments list.")
        return render(request, 'invoices/payment_list.html', {'page_obj': None, 'search_query': search_query})





        
# View for adding a new payment
@login_required
@permission_required('dashapp.add_payment', raise_exception=True)
def add_payment(request):
    """
    View to add a new payment.
    """
    students = Student.objects.all()
    classes = Glass.objects.all()

    try:
        if request.method == 'POST':
            form = PaymentForm(request.POST)
            if form.is_valid():
                student_id = request.POST.get('transaction_student')
                student_class_id = request.POST.get('transaction_student_class')

                student = get_object_or_404(Student, pk=student_id)
                student_class = get_object_or_404(Glass, pk=student_class_id)
                
                # Get or create the transaction
                transaction, created = Transaction.objects.get_or_create(
                    student=student,
                    student_class=student_class
                )
                
                # Create the payment and associate it with the transaction
                payment = form.save(commit=False)
                payment.transaction = transaction
                payment.save()
                
                log_activity(request, 'added payment', 'payment', payment.id)  # Log the activity
                messages.success(request, 'Payment added successfully!')
                return redirect('payments_list')
        else:
            form = PaymentForm()

        return render(request, 'invoices/add_payment.html', {'form': form, 'students': students, 'classes': classes})

    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while adding the payment.")
        return render(request, 'invoices/add_payment.html', {'form': form, 'students': students, 'classes': classes})


# View for updating an existing payment
@login_required
@permission_required('dashapp.change_payment', raise_exception=True)
def update_payment(request, payment_id):
    """
    View to update an existing payment.
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        form = PaymentForm(request.POST or None, instance=payment)
        
        students = Student.objects.all()
        classes = Glass.objects.all()

        if form.is_valid():
            form.save()
            log_activity(request, 'updated payment', 'payment', payment.id)  # Log the activity
            messages.success(request, 'Payment updated successfully!')
            return redirect('payments_list')

        return render(request, 'invoices/update_payment.html', {
            'form': form,
            'students': students,
            'classes': classes,
        })
    
    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while updating the payment.")
        return render(request, 'invoices/update_payment.html', {
            'form': form,
            'students': students,
            'classes': classes,
        })









# View for listing all expenses with search, category filter, and pagination
@login_required
@permission_required('dashapp.view_expense', raise_exception=True)
def expense_list(request):
    """
    View to list all expenses with search and category filter functionality.
    """
    try:
        search_query = request.GET.get('q', '')
        selected_category = request.GET.get('category', '')
        expenses = Expense.objects.all().order_by('-created_at')

        # Filter by search query
        if search_query:
            expenses = expenses.filter(expense_name__icontains=search_query).order_by('-created_at')

        # Filter by selected category
        if selected_category:
            expenses = expenses.filter(category=selected_category).order_by('-created_at')

        # Pagination
        paginator = Paginator(expenses, 10)  # Show 10 expenses per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Pass category choices to the template
        category_choices = Expense.CATEGORY_CHOICES

       


        context = {
            'expenses': expenses,
            'page_obj': page_obj,
            'search_query': search_query,
            'selected_category': selected_category,
            'category_choices': category_choices,
        }

        return render(request, 'expenses/expense_list.html', context)

    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while loading the expense list.")
        return render(request, 'expenses/expense_list.html', {
            'expenses': None,
            'page_obj': None,
            'search_query': search_query,
            'selected_category': selected_category,
            'category_choices': Expense.CATEGORY_CHOICES
        })


# View for adding a new expense
@login_required
@permission_required('dashapp.add_expense', raise_exception=True)
def add_expense(request):
    """
    View to add a new expense.
    """
    try:
        if request.method == 'POST':
            form = ExpenseForm(request.POST)
            if form.is_valid():
                form.save()
                log_activity(request, 'added expense', 'expense', None)  # Log the activity
                messages.success(request, "Expense added successfully.")
                return redirect('expense_list')
        else:
            form = ExpenseForm()

        return render(request, 'expenses/add_expense.html', {'form': form})

    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while adding the expense.")
        return render(request, 'expenses/add_expense.html', {'form': form})


# View for updating an existing expense
@login_required
@permission_required('dashapp.change_expense', raise_exception=True)
def update_expense(request, expense_id):
    """
    View to update an existing expense.
    """
    try:
        expense = get_object_or_404(Expense, pk=expense_id)

        if request.method == 'POST':
            form = ExpenseForm(request.POST, instance=expense)
            if form.is_valid():
                form.save()
                log_activity(request, 'updated expense', 'expense', expense.id)  # Log the activity
                messages.success(request, "Expense updated successfully.")
                return redirect('expense_list')
            else:
                print(form.errors)
        else:
            form = ExpenseForm(instance=expense)

        return render(request, 'expenses/update_expense.html', {'form': form})

    except Exception as e:
        log_error(request, e)  # Log any errors
        messages.error(request, "An error occurred while updating the expense.")
        return render(request, 'expenses/update_expense.html', {'form': form, 'expense': expense})






@login_required
@permission_required('dashapp.view_student', raise_exception=True)
def student_report(request):
    search_query = request.GET.get('search', '')
    class_filter = request.GET.get('class', '')
    status_filter = request.GET.get('status', '')
    start_date = request.GET.get('startDate', '')
    end_date = request.GET.get('endDate', '')

    try:
        students_query = Student.objects.filter(status='Active')

        if search_query:
            students_query = students_query.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        if class_filter:
            students_query = students_query.filter(student_class__id=class_filter).order_by('-created')
        
        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            students_query = students_query.filter(
                transaction__date_paid__range=(start_date, end_date)
            )

        paginator = Paginator(students_query, 10)  # Show 10 students per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        classes = Glass.objects.all().order_by('-created')  # Assuming you have a model named Class for student classes
        log_activity(request, action="Viewed Student Report", content_type="Student", object_id=None)



        return render(request, 'reports/student_report.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'classes': classes,
            'selected_class': class_filter,
            'status_filter': status_filter,
            'start_date': start_date,
            'end_date': end_date,
        })
    except Exception as e:
        log_error(request, e)
        return render(request, 'reports/student_report.html', {
            'error': 'An error occurred while fetching the student reports.'
        })
