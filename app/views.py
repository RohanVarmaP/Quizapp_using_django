from django.shortcuts import render, redirect
import requests
from django.contrib import messages

API_BASE_URL = 'http://127.0.0.1:8000/api/'  # Adjust to match your DRF server

def login_view(request):
    token = request.session.get('token')
    print(token)
    if token:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            response = requests.post(API_BASE_URL + 'login/', data={
                'username': username,
                'password': password
            })
            if response.status_code == 200:
                data = response.json()
                request.session['token'] = data['token']
                request.session['username'] = data['username']
                request.session['user_id'] = data['user_id']
                request.session['role'] = data.get('role')
                print(request.session['role'])
                return redirect('home')
            else:
                messages.error(request, "Invalid Credentials")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Login failed: {e}")
            return redirect('login')

    return render(request, 'app/login.html')

def logout_view(request):
    token = request.session.get('token')
    if token:
        headers = {'Authorization': f'Token {token}'}
        try:
            requests.post(API_BASE_URL + 'logout/', headers=headers)
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Logout failed: {e}")
    request.session.flush()
    return redirect('login')

def home_view(request):
    token = request.session.get('token')
    if not token:
        return redirect('login')

    headers = {'Authorization': f'Token {token}'}
    try:
        response = requests.get(API_BASE_URL + 'home/', headers=headers)
        data = response.json()
        print(data)
        return render(request, 'app/home.html', {'data': data})
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Could not load home: {e}")
        return redirect('login')

def quiz_view(request, quiz_id):
    token = request.session.get('token')
    role = request.session.get('role')
    if not token:
        return redirect('login')

    headers = {'Authorization': f'Token {token}'}

    if request.method == 'GET':
        try:
            response = requests.get(API_BASE_URL + f'quiz/{quiz_id}/', headers=headers)
            if response.status_code == 200:
                quiz_data = response.json()
                return render(request, 'app/quiz.html', {'quiz': quiz_data})
            messages.error(request, "Quiz not found.")
            return redirect('home')
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not load quiz: {e}")
            return redirect('home')

    elif request.method == 'POST':
        if role != 'student' :
            messages.error(request, "Only students can submit quizzes.")
            return redirect('quiz', quiz_id=quiz_id)
        answers = []
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                answers.append({
                    'question_id': question_id,
                    'useranswer': value
                })
        try:
            response = requests.post(
                API_BASE_URL + f'quiz/{quiz_id}/submit/',
                headers=headers,
                json={'answers': answers}
            )
            if response.status_code == 200:
                return redirect('rank', quiz_id=quiz_id)
            messages.error(request, "Failed to submit quiz.")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Quiz submission failed: {e}")
        return redirect('home')

    return redirect('home')

def quiz_marks_view(request, quiz_id):
    token = request.session.get('token')
    headers = {'Authorization': f'Token {token}'}
    try:
        response = requests.get(API_BASE_URL + f'quiz/{quiz_id}/marks/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(data)
            return render(request, 'app/rank.html', {'data': data})
        messages.error(request, "Could not fetch quiz marks.")
        return redirect('home')
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Could not fetch quiz marks: {e}")
        return redirect('home')
    
def review_quiz_view(request, quiz_id):
    token = request.session.get('token')
    if not token:
        return redirect('login')

    headers = {'Authorization': f'Token {token}'}

    if request.method == 'GET':
        try:
            response = requests.get(API_BASE_URL + f'quiz/{quiz_id}/view/', headers=headers)
            if response.status_code == 200:
                quiz_data = response.json()
                return render(request, 'app/quiz_result.html', {'quiz': quiz_data})
            messages.error(request, "Quiz not found.")
            return redirect('home')
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not load quiz: {e}")
            return redirect('home')
    return redirect('home')