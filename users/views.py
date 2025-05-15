from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import CustomUser, Role
from .forms import CustomUserCreationForm, TeamMemberForm

def is_admin(user):
    return user.is_authenticated and user.role == Role.ADMIN

# @login_required
def dashboard(request):
    # return HttpResponse("Welcome to the dashboard!")
    return render(request, 'users/dashboard.html')

# @user_passes_test(is_admin)
def add_team_member(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Generate a random password and set it
            # password = CustomUser.objects.make_random_password()
            # user.set_password(password)
            user.save()
            # TODO: Send email with temporary password
            return redirect('team_members')
    else:
        form = TeamMemberForm()
    
    return render(request, 'users/add_team_member.html', {'form': form})

class TeamMemberListView(ListView):
    model = CustomUser
    template_name = 'users/team_members.html'
    context_object_name = 'team_members'
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        return CustomUser.objects.exclude(pk=self.request.user.pk)