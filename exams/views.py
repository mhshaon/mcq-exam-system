import csv
import io
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .models import Exam, Question, Choice, ExamSession, Answer
from .forms import ExamForm, QuestionUploadForm, QuestionWithChoicesForm


def home(request):
    """Home page - redirect based on user role"""
    if request.user.is_authenticated:
        return redirect('exams:dashboard')
    return render(request, 'exams/home.html')


@login_required
def dashboard(request):
    """Dashboard based on user role"""
    user = request.user
    
    if user.is_admin():
        # Admin dashboard
        exams = Exam.objects.all().order_by('-created_at')
        context = {
            'exams': exams,
            'user_role': 'admin'
        }
    elif user.is_examiner():
        # Examiner dashboard
        exams = Exam.objects.filter(examiner=user).order_by('-created_at')
        context = {
            'exams': exams,
            'user_role': 'examiner'
        }
    else:
        # Examinee dashboard
        sessions = ExamSession.objects.filter(examinee=user).order_by('-started_at')
        context = {
            'sessions': sessions,
            'user_role': 'examinee'
        }
    
    return render(request, 'exams/dashboard.html', context)


@login_required
def create_exam(request):
    """Create a new exam (Examiner only)"""
    if not request.user.is_examiner() and not request.user.is_admin():
        raise PermissionDenied("Only examiners can create exams.")
    
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.examiner = request.user
            exam.save()
            messages.success(request, f'Exam "{exam.title}" created successfully!')
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = ExamForm()
    
    return render(request, 'exams/create_exam.html', {'form': form})


@login_required
def exam_detail(request, exam_id):
    """View exam details"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Check permissions
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to view this exam.")
    
    questions = exam.questions.all().order_by('order')
    sessions = exam.sessions.all().order_by('-started_at')
    
    context = {
        'exam': exam,
        'questions': questions,
        'sessions': sessions,
    }
    return render(request, 'exams/exam_detail.html', context)


@login_required
def edit_exam(request, exam_id):
    """Edit exam details"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to edit this exam.")
    
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam updated successfully!')
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = ExamForm(instance=exam)
    
    return render(request, 'exams/edit_exam.html', {'form': form, 'exam': exam})


@login_required
def upload_questions(request, exam_id):
    """Upload questions via CSV file"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to upload questions for this exam.")
    
    if request.method == 'POST':
        form = QuestionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            # Read CSV file
            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                questions_created = 0
                with transaction.atomic():
                    for row in reader:
                        # Create question
                        question = Question.objects.create(
                            exam=exam,
                            text=row['question'],
                            order=questions_created + 1
                        )
                        
                        # Create choices
                        for i in range(1, 6):  # 5 choices (A, B, C, D, E)
                            choice_text = row.get(f'option_{i}', '')
                            if choice_text:
                                is_correct = row.get('correct_answer', '').strip() == str(i)
                                Choice.objects.create(
                                    question=question,
                                    text=choice_text,
                                    is_correct=is_correct
                                )
                        
                        questions_created += 1
                
                exam.num_questions = questions_created
                exam.save()
                
                messages.success(request, f'Successfully uploaded {questions_created} questions!')
                return redirect('exams:exam_detail', exam_id=exam.id)
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        form = QuestionUploadForm()
    
    return render(request, 'exams/upload_questions.html', {'form': form, 'exam': exam})


def join_exam(request):
    """Join an exam using exam code"""
    if request.method == 'POST':
        exam_code = request.POST.get('exam_code', '').strip().upper()
        
        try:
            exam = Exam.objects.get(code=exam_code, is_published=True)
            
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to join the exam.')
                return redirect('account_login')
            
            if not request.user.is_examinee() and not request.user.is_admin():
                messages.error(request, 'Only examinees can take exams.')
                return redirect('exams:dashboard')
            
            # Check if exam is still active
            now = timezone.now()
            if exam.end_time and now > exam.end_time:
                messages.error(request, 'This exam has ended.')
                return redirect('exams:join_exam')
            
            if exam.start_time and now < exam.start_time:
                # Store exam info in session for display
                request.session['pending_exam'] = {
                    'title': exam.title,
                    'code': exam.code,
                    'start_time': exam.start_time.isoformat(),
                    'description': exam.description,
                    'duration': exam.duration_minutes
                }
                return redirect('exams:exam_pending', exam_code=exam_code)
            
            return redirect('exams:take_exam', exam_code=exam_code)
            
        except Exam.DoesNotExist:
            messages.error(request, 'Invalid exam code.')
    
    return render(request, 'exams/join_exam.html')


def exam_pending(request, exam_code):
    """Show exam pending page with countdown timer"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to view exam details.')
        return redirect('account_login')
    
    if not request.user.is_examinee() and not request.user.is_admin():
        messages.error(request, 'Only examinees can view exam details.')
        return redirect('exams:dashboard')
    
    # Get exam info from session
    pending_exam = request.session.get('pending_exam')
    if not pending_exam or pending_exam['code'] != exam_code:
        messages.error(request, 'Invalid exam session.')
        return redirect('exams:join_exam')
    
    # Get exam from database for additional info
    try:
        exam = Exam.objects.get(code=exam_code, is_published=True)
    except Exam.DoesNotExist:
        messages.error(request, 'Exam not found.')
        return redirect('exams:join_exam')
    
    context = {
        'exam': exam,
        'pending_exam': pending_exam,
        'start_time': exam.start_time,
        'start_time_iso': exam.start_time.isoformat() if exam.start_time else None,
        'current_time': timezone.now(),
        'current_time_iso': timezone.now().isoformat()
    }
    
    return render(request, 'exams/exam_pending.html', context)


@login_required
def take_exam(request, exam_code):
    """Take an exam"""
    exam = get_object_or_404(Exam, code=exam_code, is_published=True)
    
    if not request.user.is_examinee() and not request.user.is_admin():
        raise PermissionDenied("Only examinees can take exams.")
    
    # Check if exam is still active
    now = timezone.now()
    if exam.end_time and now > exam.end_time:
        messages.error(request, 'This exam has ended.')
        return redirect('exams:join_exam')
    
    if exam.start_time and now < exam.start_time:
        messages.error(request, 'This exam has not started yet.')
        return redirect('exams:join_exam')
    
    # Check if user already has a session for this exam
    session, created = ExamSession.objects.get_or_create(
        exam=exam,
        examinee=request.user,
        defaults={'started_at': timezone.now()}
    )
    
    if session.is_submitted:
        messages.info(request, 'You have already submitted this exam.')
        return redirect('exams:view_result', exam_code=exam_code)
    
    if not session.is_active():
        messages.error(request, 'Your exam session has expired.')
        return redirect('exams:join_exam')
    
    questions = exam.questions.all().order_by('order')
    
    context = {
        'exam': exam,
        'session': session,
        'questions': questions,
    }
    return render(request, 'exams/take_exam.html', context)


@login_required
def start_exam(request, exam_code):
    """Start the exam (AJAX endpoint)"""
    exam = get_object_or_404(Exam, code=exam_code)
    session, created = ExamSession.objects.get_or_create(
        exam=exam,
        examinee=request.user,
        defaults={'started_at': timezone.now()}
    )
    
    return JsonResponse({
        'success': True,
        'session_id': session.id,
        'started_at': session.started_at.isoformat(),
        'duration_minutes': exam.duration_minutes
    })


@login_required
def submit_exam(request, exam_code):
    """Submit exam answers"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    exam = get_object_or_404(Exam, code=exam_code)
    session = get_object_or_404(ExamSession, exam=exam, examinee=request.user)
    
    if session.is_submitted:
        return JsonResponse({'success': False, 'error': 'Exam already submitted'})
    
    if not session.is_active():
        return JsonResponse({'success': False, 'error': 'Exam session expired'})
    
    # Process answers
    answers_data = request.POST.get('answers', '{}')
    import json
    try:
        answers = json.loads(answers_data)
    except:
        return JsonResponse({'success': False, 'error': 'Invalid answers format'})
    
    total_correct = 0
    total_questions = 0
    
    with transaction.atomic():
        for question_id, choice_id in answers.items():
            try:
                question = Question.objects.get(id=question_id, exam=exam)
                choice = Choice.objects.get(id=choice_id, question=question)
                
                is_correct = choice.is_correct
                if is_correct:
                    total_correct += 1
                
                Answer.objects.update_or_create(
                    session=session,
                    question=question,
                    defaults={
                        'chosen_choice': choice,
                        'is_correct': is_correct
                    }
                )
                total_questions += 1
                
            except (Question.DoesNotExist, Choice.DoesNotExist):
                continue
        
        # Update session
        session.is_submitted = True
        session.completed_at = timezone.now()
        session.total_questions = total_questions
        session.total_correct = total_correct
        session.score = (total_correct / total_questions * 100) if total_questions > 0 else 0
        session.save()
    
    return JsonResponse({
        'success': True,
        'score': session.score,
        'total_correct': total_correct,
        'total_questions': total_questions
    })


@login_required
def view_result(request, exam_code):
    """View exam result"""
    exam = get_object_or_404(Exam, code=exam_code)
    session = get_object_or_404(ExamSession, exam=exam, examinee=request.user)
    
    if not session.is_submitted:
        messages.error(request, 'You have not submitted this exam yet.')
        return redirect('exams:take_exam', exam_code=exam_code)
    
    # Check if results are published (for examinees)
    if request.user.is_examinee() and not exam.results_published:
        messages.info(request, 'Results are not yet published by the examiner. Please wait for the examiner to publish the results.')
        return redirect('exams:exam_history')
    
    answers = session.answers.all().select_related('question', 'chosen_choice')
    
    context = {
        'exam': exam,
        'session': session,
        'answers': answers,
    }
    return render(request, 'exams/view_result.html', context)


@login_required
def exam_history(request):
    """View exam history for examinee"""
    if not request.user.is_examinee() and not request.user.is_admin():
        raise PermissionDenied("Only examinees can view exam history.")
    
    sessions = ExamSession.objects.filter(examinee=request.user, is_submitted=True).select_related('exam').order_by('-completed_at')
    return render(request, 'exams/exam_history.html', {'sessions': sessions})


@login_required
def manage_questions(request, exam_id):
    """Manage questions for an exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to manage questions for this exam.")
    
    questions = exam.questions.all().order_by('order')
    
    if request.method == 'POST':
        # Handle question reordering or deletion
        pass
    
    return render(request, 'exams/manage_questions.html', {'exam': exam, 'questions': questions})


@login_required
def delete_all_questions(request, exam_id):
    """Delete all questions for an exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to delete questions for this exam.")
    
    if request.method == 'POST':
        # Get count of questions before deletion
        questions_count = exam.questions.count()
        
        # Delete all questions (choices will be deleted automatically due to CASCADE)
        with transaction.atomic():
            exam.questions.all().delete()
            
            # Update exam question count
            exam.num_questions = 0
            exam.save()
        
        messages.success(request, f'Successfully deleted {questions_count} questions from "{exam.title}".')
        return redirect('exams:manage_questions', exam_id=exam.id)
    
    # If GET request, show confirmation page
    questions_count = exam.questions.count()
    return render(request, 'exams/delete_all_questions_confirm.html', {
        'exam': exam, 
        'questions_count': questions_count
    })


@login_required
def edit_question(request, exam_id, question_id):
    """Edit an individual question"""
    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id, exam=exam)
    
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to edit questions for this exam.")
    
    if request.method == 'POST':
        form = QuestionWithChoicesForm(request.POST, question=question)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Question {question.order} updated successfully.')
                return redirect('exams:manage_questions', exam_id=exam.id)
            except Exception as e:
                messages.error(request, f'Error updating question: {str(e)}')
    else:
        form = QuestionWithChoicesForm(question=question)
    
    return render(request, 'exams/edit_question.html', {
        'form': form,
        'exam': exam,
        'question': question
    })


@login_required
def delete_question(request, exam_id, question_id):
    """Delete an individual question"""
    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id, exam=exam)
    
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to delete questions for this exam.")
    
    if request.method == 'POST':
        question_order = question.order
        question.delete()
        
        # Update exam question count
        exam.num_questions = exam.questions.count()
        exam.save()
        
        messages.success(request, f'Question {question_order} deleted successfully.')
        return redirect('exams:manage_questions', exam_id=exam.id)
    
    # If GET request, show confirmation page
    return render(request, 'exams/delete_question_confirm.html', {
        'exam': exam,
        'question': question
    })


@login_required
def publish_exam(request, exam_id):
    """Publish/unpublish an exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to publish this exam.")
    
    exam.is_published = not exam.is_published
    exam.save()
    
    status = "published" if exam.is_published else "unpublished"
    messages.success(request, f'Exam {status} successfully!')
    
    return redirect('exams:exam_detail', exam_id=exam.id)


@login_required
def exam_results(request, exam_id):
    """View exam results (Examiner)"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to view results for this exam.")
    
    sessions = exam.sessions.filter(is_submitted=True).order_by('-completed_at')
    
    return render(request, 'exams/exam_results.html', {'exam': exam, 'sessions': sessions})


@login_required
def publish_results(request, exam_id):
    """Publish results for examinees to see"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if not (request.user.is_admin() or exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to publish results for this exam.")
    
    # Publish the results
    exam.results_published = True
    exam.save()
    
    messages.success(request, 'Results published successfully! Examinees can now view their results.')
    return redirect('exams:exam_results', exam_id=exam.id)


@login_required
def session_detail(request, session_id):
    """View detailed session results"""
    session = get_object_or_404(ExamSession, id=session_id)
    
    if not (request.user.is_admin() or 
            session.examinee == request.user or 
            session.exam.examiner == request.user):
        raise PermissionDenied("You don't have permission to view this session.")
    
    answers = session.answers.all().select_related('question', 'chosen_choice')
    
    context = {
        'session': session,
        'answers': answers,
    }
    return render(request, 'exams/session_detail.html', context)


@login_required
def my_exams(request):
    """View exams created by examiner"""
    if not request.user.is_examiner() and not request.user.is_admin():
        raise PermissionDenied("Only examiners can view their exams.")
    
    exams = Exam.objects.filter(examiner=request.user).order_by('-created_at')
    return render(request, 'exams/my_exams.html', {'exams': exams})
