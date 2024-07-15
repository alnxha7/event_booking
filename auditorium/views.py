from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Auditorium
import stripe

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            auth_login(request, user)
            if user.role == 'user':
                return redirect('user_index')
            else:
                return redirect('event_host_index')
        else:
            messages.error(request, 'Invalid email or password.')

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
            return redirect('login')
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
        price = request.POST.get('price')
        images = request.FILES.get('images')

        if password1 == password2:
            if not User.objects.filter(email=email).exists():
                try:
                    user = User.objects.create_user(username=username, email=email, password=password1, role='host')
                    user.save()

                    auditorium = Auditorium.objects.create(
                        user=user,
                        location=location,
                        capacity=capacity,
                        price=price,
                        images=images,
                        approved=False
                    )
                    auditorium.save()

                    messages.success(request, 'Auditorium registration request sent for approval.')
                    return redirect('login')
                except Exception as e:
                    messages.error(request, f'An error occurred while creating the auditorium request: {e}')
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
    auditoriums = Auditorium.objects.filter(approved=True)
    context = {
        'auditoriums': auditoriums,
        'user': request.user,
    }
    return render(request, 'user_index.html', context)

def event_schedules(request):
    return render(request, 'event_schedules.html')

def user_bookings(request):
    return render(request, 'user_bookings.html')

def auditorium_list(request):
    auditoriums = Auditorium.objects.all()
    return render(request, 'auditorium_list.html', {
        'auditoriums': auditoriums,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    })

@csrf_exempt
def create_checkout_session(request, auditorium_id):
    auditorium = Auditorium.objects.get(pk=auditorium_id)
    success_url = f"{request.scheme}://{request.get_host()}/success/"
    cancel_url = f"{request.scheme}://{request.get_host()}/cancel/"

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': auditorium.user.username,
                    },
                    'unit_amount': int(auditorium.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return JsonResponse({'sessionId': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def capture_payment(request, session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent = session.payment_intent
        stripe.PaymentIntent.capture(payment_intent)
        return JsonResponse({'status': 'success'})
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)})

def success_view(request):
    return render(request, 'success.html')

def cancel_view(request):
    return render(request, 'cancel.html')
