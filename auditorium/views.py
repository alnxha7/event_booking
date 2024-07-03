from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .models import User, Auditorium
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

User = get_user_model()

def home(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print(f"POST data - Email: {email}, Password: {password}")  # Debugging line
        
        try:
            user = User.objects.get(email=email)
            print(f"User found: {user}")  # Debugging line
            user = authenticate(request, username=user.username, password=password)
            print(f"Authenticated User: {user}")  # Debugging line
        except User.DoesNotExist:
            user = None
            print("User not found")  # Debugging line
        
        if user is not None:
            auth_login(request, user)
            if user.role == 'host':
                return redirect('event_host_index')
            else:
                return redirect('user_index')
        else:
            messages.error(request, 'Invalid email or password.')
            print("Invalid email or password")  # Debugging line

    return render(request, 'login.html')

def register_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.create_user(email=email, username=username, password=password, role='user')
            messages.success(request, 'User registered successfully.')
            return redirect('login')  # Replace with your login URL name
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'register_user.html')

def register_auditorium(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Consider using this for auditorium name
        email = request.POST.get('email')
        password = request.POST.get('password')
        location = request.POST.get('location')
        capacity = request.POST.get('capacity')
        features = request.POST.get('features')
        price = request.POST.get('price')
        ac = request.POST.get('ac_status')  # Updated to match the field name in the HTML form

        if username and email and password and location and capacity and features and price and ac:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email is already registered.')
            else:
                hashed_password = make_password(password)
                user = User(username=username, email=email, role='host', password=hashed_password)
                user.save()

                auditorium = Auditorium(user=user, location=location, capacity=capacity, features=features, price=price, ac=ac)
                auditorium.save()

                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'All fields are required.')

    return render(request, 'register_auditorium.html')

def user_index(request):
    return render(request, 'user_index.html')

def event_host_index(request):
    return render(request, 'event_host_index.html')

def user_bookings(request):
    return render(request, 'user_bookings.html')

def event_schedules(request):
    return render(request, 'event_schedules.html')
