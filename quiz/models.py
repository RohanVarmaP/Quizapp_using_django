from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
# Create your models here.
class RoleTable(models.Model):
    role_id=models.UUIDField(editable=False,primary_key=True,default=uuid.uuid4)
    role_name=models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.role_name

class UserTable(AbstractUser):
    user_id=models.UUIDField(editable=False,default=uuid.uuid4,primary_key=True)
    role=models.ForeignKey(RoleTable,on_delete=models.CASCADE,null=True,blank=True)

class QuizTable(models.Model):
    quiz_id=models.UUIDField(editable=False,primary_key=True,default=uuid.uuid4)
    quiz_name=models.CharField(max_length=100,unique=True)
    quiz_published=models.BooleanField(default=False)
    questions = models.ManyToManyField('QuestionTable', through='QuestionsinQuizTable')

    def __str__(self):
        return self.quiz_name

class QuestionTable(models.Model):
    question_id=models.UUIDField(editable=False,primary_key=True,default=uuid.uuid4)
    question=models.TextField()
    ANSWER_CHOICES = [('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')]
    answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    option_a=models.TextField()
    option_b=models.TextField()
    option_c=models.TextField()
    option_d=models.TextField()

    def __str__(self):
        return f'Q:{self.question}, A: {self.answer}'

class QuestionsinQuizTable(models.Model):
    qinq_id=models.UUIDField(editable=False,primary_key=True,default=uuid.uuid4)
    quiz=models.ForeignKey(QuizTable,on_delete=models.CASCADE)
    question=models.ForeignKey(QuestionTable,on_delete=models.CASCADE)

    class Meta:
        unique_together=('quiz','question')

    def __str__(self):
        return f'Quiz:{self.quiz}, Question: {self.question}'

class UserAnswerTable(models.Model):
    answer_id=models.UUIDField(editable=False,primary_key=True,default=uuid.uuid4)
    CORRECT_ANSWER_CHOICES = [('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')]
    useranswer=models.CharField(max_length=1, choices=CORRECT_ANSWER_CHOICES)
    user=models.ForeignKey(UserTable,on_delete=models.CASCADE)
    quiz=models.ForeignKey(QuizTable,on_delete=models.CASCADE)
    question=models.ForeignKey(QuestionTable,on_delete=models.CASCADE)

    class Meta:
        unique_together =('user','quiz','question')

    def __str__(self):
        return f'Quiz:{self.quiz}, Question: {self.question}, User_answer: {self.useranswer}'
    
class MarksTable(models.Model):
    marks_id=models.UUIDField(editable=False,primary_key=True,default=uuid.uuid4)
    marks = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    user=models.ForeignKey(UserTable,on_delete=models.CASCADE)
    quiz=models.ForeignKey(QuizTable,on_delete=models.CASCADE)

    class Meta:
        unique_together=('user','quiz')

    def __str__(self):
        return f'Quiz:{self.quiz}, User: {self.user}, Marks: {self.marks}'

class AttendedQuizTable(models.Model):
    aq_id=models.UUIDField(editable=False,primary_key=True,default=uuid.uuid4)
    user=models.ForeignKey(UserTable,on_delete=models.CASCADE)
    quiz=models.ForeignKey(QuizTable,on_delete=models.CASCADE)

    class Meta:
        unique_together=('user','quiz')

    def __str__(self):
        return f'Quiz:{self.quiz}, User: {self.user}'