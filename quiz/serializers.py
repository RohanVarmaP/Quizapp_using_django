from rest_framework import serializers
from .models import (RoleTable,UserTable,QuizTable,QuestionTable,
                     QuestionsinQuizTable,UserAnswerTable,
                     MarksTable,AttendedQuizTable)


#readonly serializers
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model= RoleTable
        fields=['role_id','role_name']
        read_only_fields = fields

class UserSerializer(serializers.ModelSerializer):
    role=RoleSerializer(read_only=True)
    class Meta:
        model=UserTable
        fields=['user_id','username','email','role']
        read_only_fields = fields
        
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model= QuizTable
        fields = ['quiz_id', 'quiz_name', 'quiz_published', 'questions']
        read_only_fields = fields

class StudentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=QuestionTable
        fields=['question_id', 'question', 'option_a', 'option_b', 'option_c', 'option_d']
        read_only_fields = fields

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model= QuestionTable
        fields=['question_id', 'question','answer', 'option_a', 'option_b', 'option_c', 'option_d']
        read_only_fields = fields

class QuestioninQuizSerializer(serializers.ModelSerializer):
    quiz=QuizSerializer(read_only=True)
    question=QuestionSerializer(read_only=True)

    class Meta:
        model=QuestionsinQuizTable
        fields='__all__'
        read_only_fields = fields

#read and write enabled classes

class UserAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model=UserAnswerTable
        fields=['useranswer']

    #validate answer format (A/B/C/D)
    def validate_useranswer(self, value):
        if value not in ['A', 'B', 'C', 'D']:
            raise serializers.ValidationError("Answer must be one of: A, B, C, D.")
        return value

class MarksSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    quiz=QuizSerializer()

    class Meta:
        model=MarksTable
        fields='__all__'
    
    #validate answer format (A/B/C/D)
    def validate_useranswer(self, value):
        if not (0<=value<=100):
            raise serializers.ValidationError("Marks must be in between 0 to 100.")
        return value

class AttendedQuizSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    quiz=QuizSerializer()

    class Meta:
        model=AttendedQuizTable
        fields='__all__'
    
    def validate(self, data):
        # Prevent duplicate attendance records
        if AttendedQuizTable.objects.filter(user=data['user'], quiz=data['quiz']).exists():
            raise serializers.ValidationError("User has already attended this quiz.")
        return data

#serializers for quiz page
#Pulls all questions linked to a quiz through QuestionsinQuizTable
class QuizQuestionSerializer(serializers.ModelSerializer):
    question = StudentQuestionSerializer()

    class Meta:
        model = QuestionsinQuizTable
        # fields='__all__'
        fields = ['question']
#This brings it all together
class QuizPageSerializer(serializers.Serializer):
    username = serializers.CharField(source='user.username')
    quiz_name = serializers.CharField(source='quiz.quiz_name')
    questions = serializers.SerializerMethodField()

    def get_questions(self, obj):
        # obj is a dict with 'user' and 'quiz'
        quiz = obj['quiz']
        questions_links = QuestionsinQuizTable.objects.filter(quiz=quiz).select_related('question')
        return QuizQuestionSerializer(questions_links, many=True).data


#serializers for Home page

class UserHomePageSerializer(serializers.Serializer):
    username = serializers.CharField()
    attended_quizzes = serializers.SerializerMethodField()
    not_attended_quizzes = serializers.SerializerMethodField()

    def get_attended_quizzes(self, user):
        attended_quiz_ids = AttendedQuizTable.objects.filter(user=user).values_list('quiz_id', flat=True)
        quizzes = QuizTable.objects.filter(quiz_id__in=attended_quiz_ids, quiz_published=True)
        return QuizSerializer(quizzes, many=True).data

    def get_not_attended_quizzes(self, user):
        attended_quiz_ids = AttendedQuizTable.objects.filter(user=user).values_list('quiz_id', flat=True)
        quizzes = QuizTable.objects.filter(quiz_published=True).exclude(quiz_id__in=attended_quiz_ids)
        return QuizSerializer(quizzes, many=True).data


#serializer for Ranking page
class QuizMarksSummarySerializer(serializers.Serializer):
    quiz_name = serializers.CharField()
    results = serializers.SerializerMethodField()

    def get_results(self, quiz):
        marks = MarksTable.objects.filter(quiz=quiz).select_related('user').order_by('-marks')
        return MarksSerializer(marks, many=True).data

#Pulls the questions,answers and user_given_answer linked to a quiz
class AnsweredQuizPageSerializer(serializers.Serializer):
    username = serializers.CharField(source='user.username')
    quiz_name = serializers.CharField(source='quiz.quiz_name')
    questions = serializers.SerializerMethodField()

    def get_questions(self, obj):
        quiz = obj['quiz']
        user = obj['user']

        # Get the questions in the quiz
        questions_links = QuestionsinQuizTable.objects.filter(quiz=quiz).select_related('question')

        result = []
        for link in questions_links:
            question = link.question

            # Fetch the user's answer for this question
            try:
                user_answer = UserAnswerTable.objects.get(user=user, question=question)
                user_answer_data = UserAnswerSerializer(user_answer).data
            except UserAnswerTable.DoesNotExist:
                user_answer_data = None  # or {'selected_answer': None}

            result.append({
                'question': QuestionSerializer(question).data,
                'user_answer': user_answer_data,
            })

        return result
