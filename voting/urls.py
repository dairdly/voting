"""voting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from main.views import (
    RegFormView, 
    VoteFormView, 
    ThanksView, 
    CandidateRegistrationView,
    PositionRegistrationView,
    PositionAndCandidateList,
    DeletePosition,
    DeleteCandidate,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RegFormView.as_view(), name="home"),
    path('vote/', VoteFormView.as_view(), name="vote"),
    path('thanks/', ThanksView.as_view(), name="thanks"),
    path('register/candidate/', CandidateRegistrationView.as_view(), name="register_candidate"),
    path('register/position/', PositionRegistrationView.as_view(), name="register_position"),
    path('list/', PositionAndCandidateList.as_view(), name="list"),
    path('position/<pk>/delete/', DeletePosition, name="delete_position"),
    path('candidate/<pk>/delete/', DeleteCandidate, name="delete_candidate"),
]
