"""voting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.reg, name='reg')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='reg')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    AccessCodeView,
    LogoutView,
    ManageElectionView,
    VotersListView,
    CancelElectionView,
    ResultView,
    ChangeAccessCodeView,
    ChangeStaffCodeView,
    ChangeAdminCodeView,
)


urlpatterns = [
    path('', RegFormView.as_view(), name="reg"),
    path('vote/', VoteFormView.as_view(), name="vote"),
    path('thanks/', ThanksView.as_view(), name="thanks"),
    path('register/candidate/', CandidateRegistrationView.as_view(), name="register_candidate"),
    path('register/position/', PositionRegistrationView.as_view(), name="register_position"),
    path('list/', PositionAndCandidateList.as_view(), name="list"),
    path('position/<pk>/delete/', DeletePosition.as_view(), name="delete_position"),
    path('candidate/<pk>/delete/', DeleteCandidate.as_view(), name="delete_candidate"),
    path('auth/', AccessCodeView.as_view(), name="access_code"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('manage/', ManageElectionView.as_view(), name='manage'),
    path('vlist/', VotersListView.as_view(), name='vlist'),
    path('del/', CancelElectionView.as_view(), name='cancel-election'),
    path('result/', ResultView.as_view(), name='result'),
    path('access/', ChangeAccessCodeView.as_view(), name='change-codes'), 
    path('staff/', ChangeStaffCodeView.as_view(), name='change-staff-code'),
    path('admin/', ChangeAdminCodeView.as_view(), name='change-admin-code'),
]
