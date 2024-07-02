from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .models import User
from django.contrib.auth.hashers import check_password

def home(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                auth_login(request, user)
                if user.role == 'user':
                    return redirect('user_index')
                elif user.role == 'host':
                    return redirect('event_host_index')
                else:
                    messages.error(request, 'Invalid role')
            else:
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')

    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if username and email and password:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email is already registered.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'All fields are required.')

    return render(request, 'register.html')

def user_index(request):
    return render(request, 'user_index.html')

def event_host_index(request):
    return render(request, 'event_host_index.html')

def user_bookings(request):
    return render(request, 'user_bookings.html')

def event_schedules(request):
    return render(request, 'event_schedules.html')
