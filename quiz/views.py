from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import update_last_login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import (RoleTable,UserTable,QuizTable,
                     QuestionTable,QuestionsinQuizTable,
                     UserAnswerTable,MarksTable,AttendedQuizTable)
from .serializers import (RoleSerializer,UserSerializer, 
                          QuizSerializer,QuestionSerializer, 
                          QuestioninQuizSerializer,UserAnswerSerializer,
                          MarksSerializer,AttendedQuizSerializer, 
                          UserHomePageSerializer,QuizPageSerializer, QuizMarksSummarySerializer,
                          AnsweredQuizPageSerializer)
from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # disables CSRF check


# Create your views here.
# Auth APIs
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            update_last_login(None, user)
            return Response({
                'token': token.key,
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role.role_name if hasattr(user, 'role') else None
            }, status=status.HTTP_200_OK)

        return Response({'error': "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


class SignupView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        role_name = "role"  # example: "student"

        print(username,password,role_name)

        if not username or not password or not role_name:
            return Response({"error": "Username, password, and role are required."}, status=400)

        if UserTable.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=400)

        try:
            role = RoleTable.objects.get(role_name__iexact=role_name)
        except RoleTable.DoesNotExist:
            return Response({"error": f"Role '{role_name}' not found."}, status=400)

        user = UserTable.objects.create_user(username=username, password=password, role=role)

        return Response({
            "message": "User registered successfully.",
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.role_name
        }, status=201)


#web pages for quiz
class HomePageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserHomePageSerializer(request.user)
        return Response(serializer.data)

class QuizPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            quiz = QuizTable.objects.get(quiz_id=quiz_id, quiz_published=True)
        except QuizTable.DoesNotExist:
            return Response({'error': 'Quiz not found or not published'}, status=404)

        data = {'user': request.user, 'quiz': quiz}
        serializer = QuizPageSerializer(data)
        return Response(serializer.data)

class SubmitAnswersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        user = request.user
        answers = request.data.get('answers', {})  # Expecting: [{"question_id": "xyz", "useranswer": "A"}, ...]

        try:
            quiz = QuizTable.objects.get(quiz_id=quiz_id, quiz_published=True)
        except QuizTable.DoesNotExist:
            return Response({'error': 'Quiz not found or not published'}, status=404)

        # Step 1: Check attempt status
        attempt, created = AttendedQuizTable.objects.get_or_create(user=user, quiz=quiz)

        if attempt.first and attempt.second:
            return Response({'error': 'Maximum attempts reached'}, status=403)

        # Step 2: Calculate marks
        total_questions = 0
        correct_answers = 0

        for ans in answers:
            question_id = ans.get("question_id")
            user_ans = ans.get("useranswer")
            try:
                question = QuestionTable.objects.get(question_id=question_id)
                correct = question.answer == user_ans
                total_questions += 1
                if correct:
                    correct_answers += 1

                # Save user's answer
                UserAnswerTable.objects.update_or_create(
                    user=user,
                    quiz=quiz,
                    question=question,
                    defaults={'useranswer': user_ans}
                )

            except QuestionTable.DoesNotExist:
                continue

        percentage = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0

        # Step 3: Save marks
        MarksTable.objects.update_or_create(user=user, quiz=quiz, defaults={'marks': percentage})

        # Step 4: Update attempt record
        if not attempt.first:
            attempt.first = True
        elif not attempt.second:
            attempt.second = True
        attempt.save()

        return Response({
            'message': 'Answers submitted successfully',
            'attempt': 'first' if not attempt.second else 'second',
            'score': percentage
        }, status=200)


class QuizMarksView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            quiz = QuizTable.objects.get(quiz_id=quiz_id)
        except QuizTable.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=404)

        serializer = QuizMarksSummarySerializer(quiz)
        return Response(serializer.data)

class AnsweredQuizPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            quiz = QuizTable.objects.get(quiz_id=quiz_id, quiz_published=True)
        except QuizTable.DoesNotExist:
            return Response({'error': 'Quiz not found or not published'}, status=404)
        # print("views Hellooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo") 
        # print(request.user.role)
        data = {'user': request.user, 'quiz': quiz,'role':request.user.role}
        serializer = AnsweredQuizPageSerializer(data)
        return Response(serializer.data)