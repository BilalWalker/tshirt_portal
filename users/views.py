from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import CustomUser, Role
# from .forms import CustomUserCreationForm, TeamMemberForm

def is_admin(user):
    return user.is_authenticated and user.role == Role.ADMIN

# @login_required
def dashboard(request):
    return HttpResponse("Welcome to the dashboard!")
    # return render(request, 'users/dashboard.html')

