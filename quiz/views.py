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

@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF for this view
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

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
        answers = request.data.get('answers', {})  # Expect: {"question_id": "A", ...}

        try:
            quiz = QuizTable.objects.get(quiz_id=quiz_id, quiz_published=True)
        except QuizTable.DoesNotExist:
            return Response({'error': 'Quiz not found or not published'}, status=404)

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

                # Save user answer
                UserAnswerTable.objects.update_or_create(
                    user=user,
                    quiz=quiz,
                    question=question,
                    defaults={'useranswer': user_ans}
                )

            except QuestionTable.DoesNotExist:
                continue

        # Save to MarksTable
        percentage = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        MarksTable.objects.update_or_create(user=user, quiz=quiz, defaults={'marks': percentage})

        # Add to AttendedQuizTable
        AttendedQuizTable.objects.get_or_create(user=user, quiz=quiz)

        return Response({
            'message': 'Answers submitted successfully',
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

        data = {'user': request.user, 'quiz': quiz}
        serializer = AnsweredQuizPageSerializer(data)
        return Response(serializer.data)