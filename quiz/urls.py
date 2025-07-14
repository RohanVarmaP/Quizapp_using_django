"""
URL configuration for mainapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import (
    LoginView, LogoutView,
    HomePageView, QuizPageView,
    SubmitAnswersView, QuizMarksView,
    AnsweredQuizPageView,SignupView
)

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('signup/', SignupView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('home/', HomePageView.as_view()),
    path('quiz/<uuid:quiz_id>/', QuizPageView.as_view()),  # GET
    path('quiz/<uuid:quiz_id>/submit/', SubmitAnswersView.as_view()),  # POST
    path('quiz/<uuid:quiz_id>/marks/', QuizMarksView.as_view()),  # GET
    path('quiz/<uuid:quiz_id>/view/', AnsweredQuizPageView.as_view()), #GET
]
