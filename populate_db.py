import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from onlinecourse.models import Course, Lesson, Instructor, Learner, Question, Choice, Enrollment, Submission
from django.utils.timezone import now

# 1. Superuser
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
    print("Created superuser 'admin'")
else:
    admin_user = User.objects.get(username='admin')

# 2. Student user
if not User.objects.filter(username='chetan').exists():
    student_user = User.objects.create_user(
        username='chetan',
        email='chetanagrawal721@gmail.com',
        password='password123',
        first_name='Chetan',
        last_name='Agrawal'
    )
    print("Created user 'chetan'")
else:
    student_user = User.objects.get(username='chetan')

# 3. Instructor
instructor, _ = Instructor.objects.get_or_create(
    user=admin_user,
    defaults={'full_time': True, 'total_learners': 150}
)

# 4. Course
course, created = Course.objects.get_or_create(
    name='Introduction to Cloud Development with Django',
    defaults={
        'description': 'Learn full-stack web application development using Python, Django, SQL databases, and Cloud deployment.',
        'pub_date': now().date(),
        'total_enrollment': 1
    }
)
course.instructors.add(instructor)

# 5. Lessons
lesson1, _ = Lesson.objects.get_or_create(
    title='Django Models and Migrations',
    course=course,
    defaults={
        'order': 0,
        'content': 'In this lesson, you will learn how Django ORM models represent relational database tables and how migrations propagate model changes into your database schema.'
    }
)

lesson2, _ = Lesson.objects.get_or_create(
    title='Django Views and Templates',
    course=course,
    defaults={
        'order': 1,
        'content': 'Understand HttpRequest and HttpResponse lifecycles, class-based vs function-based views, and rendering dynamic HTML using the Django Template Engine.'
    }
)

lesson3, _ = Lesson.objects.get_or_create(
    title='Django Admin and Authentication',
    course=course,
    defaults={
        'order': 2,
        'content': 'Explore the automatic Django admin site, customize ModelAdmin and Inlines, and manage user authentication with login, logout, and permissions.'
    }
)

# 6. Questions and Choices
# Clear existing questions for clean setup
Question.objects.filter(course=course).delete()

# Question 1
q1 = Question.objects.create(
    course=course,
    lesson=lesson1,
    question_text='Which command is used to generate database migration files based on changes detected in your models?',
    grade=50
)
c1_1 = Choice.objects.create(question=q1, choice_text='python manage.py makemigrations', is_correct=True)
c1_2 = Choice.objects.create(question=q1, choice_text='python manage.py migrate', is_correct=False)
c1_3 = Choice.objects.create(question=q1, choice_text='python manage.py runserver', is_correct=False)
c1_4 = Choice.objects.create(question=q1, choice_text='python manage.py createsuperuser', is_correct=False)

# Question 2
q2 = Question.objects.create(
    course=course,
    lesson=lesson2,
    question_text='Which Django template tag is required in forms using the POST method to protect against cross-site request forgery?',
    grade=50
)
c2_1 = Choice.objects.create(question=q2, choice_text='{% csrf_token %}', is_correct=True)
c2_2 = Choice.objects.create(question=q2, choice_text='{% form_token %}', is_correct=False)
c2_3 = Choice.objects.create(question=q2, choice_text='{% secure_post %}', is_correct=False)
c2_4 = Choice.objects.create(question=q2, choice_text='{% auth_key %}', is_correct=False)

# 7. Enrollment
enrollment, _ = Enrollment.objects.get_or_create(
    user=student_user,
    course=course,
    defaults={'mode': 'honor', 'rating': 5.0}
)

# 8. Submission with correct choices
submission = Submission.objects.create(enrollment=enrollment)
submission.choices.add(c1_1, c2_1)
submission.save()

print(f"Sample data populated successfully! Course ID: {course.id}, Submission ID: {submission.id}")
