from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
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

        user = authenticate(request, email=email, password=password)
        if user is not None:
            auth_login(request, user)
            print(f"Authenticated User: {user}")  # Debugging line
            if user.role == 'user':
                return redirect('user_index')
            else:
                return redirect('event_host_index')
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
            user = User.objects.create_user(email=email, username=username, password=password, role='host')
            user.save()
            messages.success(request, 'User registered successfully.')
            return redirect('login')  # Replace with your login URL name
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'register_user.html')

def register_auditorium(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        location = request.POST.get('location')
        capacity = request.POST.get('capacity')
        features = request.POST.get('features')
        price = request.POST.get('price')
        ac = request.POST.get('ac')
        images = request.FILES.get('images')

        print("Form data:", username, email, password1, password2, location, capacity, features, price, ac, images)

        if password1 == password2:
            if not User.objects.filter(email=email).exists():
                try:
                    # Create the user
                    user = User.objects.create_user(username=username, email=email, password=password1)
                    print("User created successfully:", user)  # Debugging

                    # Create the auditorium
                    Auditorium.objects.create(
                        user=user,  # Assigning the User instance to the ForeignKey field
                        location=location,
                        capacity=capacity,
                        features=features,
                        price=price,
                        ac=ac,
                        images=images
                    )
                    print("Auditorium created successfully!")  # Debugging
                    return redirect('login')  # Replace 'login' with the appropriate URL name
                except Exception as e:
                    print("Error creating auditorium:", e)  # Debugging
                    messages.error(request, 'An error occurred while creating the auditorium.')
            else:
                messages.error(request, 'Email already exists.')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'register_auditorium.html')


@login_required
def event_host_index(request):
    return render(request, 'event_host_index.html')

@login_required
def user_index(request):
    auditoriums = Auditorium.objects.all()
    print(auditoriums)
    return render(request, 'user_index.html')

def event_schedules(request):
    return render(request, 'event_schedules.html')

def user_bookings(request):
    return render(request, 'user_bookings.html')

