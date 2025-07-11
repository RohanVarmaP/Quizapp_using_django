from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('quiz/<uuid:quiz_id>/', views.quiz_view, name='quiz'),
    path('quiz/<uuid:quiz_id>/marks/', views.quiz_marks_view, name='rank'),
    path('quiz/<uuid:quiz_id>/review/', views.review_quiz_view, name='review'),
]
