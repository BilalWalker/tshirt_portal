from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('team/', views.TeamMemberListView.as_view(), name='team_members'),
    path('team/add/', views.add_team_member, name='add_team_member'),
]