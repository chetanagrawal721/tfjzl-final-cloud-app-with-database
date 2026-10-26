# GitHub Repository: tfjzl-final-cloud-app-with-database
# File: onlinecourse/views.py
# URL: https://github.com/chetanagrawal721/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
import logging

from .models import Course, Enrollment, Lesson, Instructor, Learner, Question, Choice, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except Exception:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers


def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)

    # Get or create the associated enrollment object
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    if not enrollment:
        enrollment = Enrollment.objects.create(user=user, course=course, mode='honor')

    # Create a submission object referring to the enrollment
    submission = Submission.objects.create(enrollment=enrollment)

    # Collect selected choices from exam form and associate them
    selected_choices = extract_answers(request)
    for choice_id in selected_choices:
        choice = get_object_or_404(Choice, pk=choice_id)
        submission.choices.add(choice)

    submission.save()

    # Redirect to show_exam_result with the submission id
    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result', args=(course.id, submission.id))
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    selected_ids = list(submission.choices.values_list('id', flat=True))

    total_score = 0
    possible_score = 0

    questions = course.question_set.all()
    for question in questions:
        possible_score += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade

    grade = int((total_score / possible_score) * 100) if possible_score > 0 else 0

    context = {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids,
        'submitted_choices': submission.choices.all(),
        'total_score': total_score,
        'possible_score': possible_score,
        'grade': grade,
        'possible': possible_score,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
