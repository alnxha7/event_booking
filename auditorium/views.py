from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Auditorium, Feature, AuditoriumImage, Booking, UserRequest, BookingHistory
import stripe
import json
import logging
from django.utils import timezone
from django.forms import inlineformset_factory
from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_POST
from datetime import date, timedelta, datetime

User = get_user_model()
logger = logging.getLogger(__name__)
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
        role = 'user'  # Default role for user registration

        try:
            user = User.objects.create_user(email=email, username=username, password=password, role=role)
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
    auditorium = Auditorium.objects.get(user=request.user)  # Assuming only one auditorium per user for simplicity

    AuditoriumFeatureFormset = inlineformset_factory(
        Auditorium,
        Feature,
        fields=('name', 'amount'),  # Corrected field names
        extra=1,  # Number of extra forms
    )

    if request.method == 'POST':
        formset = AuditoriumFeatureFormset(request.POST, instance=auditorium)
        if formset.is_valid():
            formset.save()
            return redirect('event_host_index')  # Redirect to the same page after submission
    else:
        formset = AuditoriumFeatureFormset(instance=auditorium)

    context = {
        'formset': formset,
        'auditorium': auditorium,
    }
    return render(request, 'event_host_index.html', context)

@login_required
def event_features(request, auditorium_id):
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    features = Feature.objects.filter(auditorium=auditorium)
    images = AuditoriumImage.objects.filter(auditorium=auditorium)

    class FeatureForm(forms.ModelForm):
        class Meta:
            model = Feature
            fields = ['name', 'amount']

    class ImageForm(forms.ModelForm):
        class Meta:
            model = AuditoriumImage
            fields = ['image']

    feature_form = FeatureForm()
    image_form = ImageForm()

    if request.method == 'POST':
        if 'add_feature' in request.POST:
            feature_form = FeatureForm(request.POST)
            if feature_form.is_valid():
                feature = feature_form.save(commit=False)
                feature.auditorium = auditorium
                feature.save()
                return redirect('event_features', auditorium_id=auditorium_id)
        elif 'add_image' in request.POST:
            image_form = ImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                image = image_form.save(commit=False)
                image.auditorium = auditorium
                image.save()
                return redirect('event_features', auditorium_id=auditorium_id)
        elif 'delete_features' in request.POST:
            feature_ids = request.POST.getlist('feature_ids')
            Feature.objects.filter(id__in=feature_ids).delete()
            return redirect('event_features', auditorium_id=auditorium_id)
        elif 'delete_images' in request.POST:
            image_ids = request.POST.getlist('image_ids')
            AuditoriumImage.objects.filter(id__in=image_ids).delete()
            return redirect('event_features', auditorium_id=auditorium_id)

    context = {
        'auditorium': auditorium,
        'features': features,
        'images': images,
        'feature_form': feature_form,
        'image_form': image_form,
    }
    return render(request, 'event_features.html', context)

@login_required
def event_schedules(request, auditorium_id):
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    bookings = Booking.objects.filter(auditorium=auditorium)
    booked_dates = {booking.date.strftime('%Y-%m-%d'): True for booking in bookings}
    booked_dates_json = json.dumps(booked_dates)
    return render(request, 'event_schedules.html', {'auditorium': auditorium, 'booked_dates_json': booked_dates_json})

@require_POST
@login_required
def manage_booking(request, auditorium_id):
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    data = json.loads(request.body)
    booking_date = data.get('date')
    book = data.get('book', False)

    if not booking_date or not isinstance(booking_date, str):
        logger.error('Invalid date format or missing date')
        return JsonResponse({'status': 'error', 'message': 'Invalid date format'}, status=400)

    try:
        booking_date = date.fromisoformat(booking_date)
    except ValueError:
        logger.error('Invalid date format')
        return JsonResponse({'status': 'error', 'message': 'Invalid date format'}, status=400)

    if booking_date < date.today():
        logger.error('Cannot book past dates')
        return JsonResponse({'status': 'error', 'message': 'Cannot book past dates'}, status=400)

    booking, created = Booking.objects.get_or_create(auditorium=auditorium, user=request.user, date=booking_date)

    if not book:
        booking.delete()
        logger.info(f'Booking for {booking_date} has been cancelled')
        return JsonResponse({'status': 'cancelled', 'message': f'Booking for {booking_date} has been cancelled'})
    else:
        logger.warning(f'Unauthorized booking attempt for {booking_date}')
        return JsonResponse({'status': 'error', 'message': 'Unauthorized booking attempt'}, status=403)
    
@login_required
def user_index(request):
    auditoriums = Auditorium.objects.filter(approved=True)
    context = {
        'auditoriums': auditoriums,
        'user': request.user,
    }
    return render(request, 'user_index.html', context)

@login_required
def user_event_schedules(request, auditorium_id):
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    bookings = Booking.objects.filter(auditorium=auditorium)
    
    # Get all booked dates for the auditorium
    booked_dates = {booking.date.strftime('%Y-%m-%d'): True for booking in bookings}

    # Calculate all dates between today and a certain number of days in the future
    start_date = date.today()
    end_date = date.today() + timedelta(days=30)  # Adjust the number of days as needed
    all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    # Determine vacant dates (dates that are not booked)
    vacant_dates = {}
    for d in all_dates:
        date_str = d.strftime('%Y-%m-%d')
        if date_str not in booked_dates:
            vacant_dates[date_str] = False  # Use False to indicate vacant dates

    vacant_dates_json = json.dumps(vacant_dates)
    return render(request, 'user_event_schedules.html', {'auditorium': auditorium, 'vacant_dates_json': vacant_dates_json})

def user_bookings(request):
    return render(request, 'user_bookings.html')

def auditorium_list(request, auditorium_id):
    auditorium = Auditorium.objects.get(id=auditorium_id)
    return render(request, 'auditorium_list.html', {'auditorium': auditorium})

def book_calendar(request, auditorium_id):
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    bookings = Booking.objects.filter(auditorium=auditorium)
    booked_dates = {booking.date.strftime('%Y-%m-%d'): True for booking in bookings}
    booked_dates_json = json.dumps(booked_dates)
    return render(request, 'book_calendar.html', {'auditorium': auditorium, 'booked_dates_json': booked_dates_json})

@login_required
def auditorium_details(request, auditorium_id):
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    features = auditorium.auditorium_features.all()
    date = request.GET.get('date')  # Fetch the date from URL query parameters

    if request.method == 'POST':
        date = request.POST.get('date')  # Ensure you are capturing the date correctly
        final_price = request.POST.get('final_price')
        selected_features = request.POST.getlist('features')

        if not date:
            messages.error(request, 'Date is required.')
            return redirect('auditorium_details', auditorium_id=auditorium_id)

        booking_request = UserRequest(
            user=request.user,
            auditorium=auditorium,
            date=date,
            final_price=final_price
        )
        booking_request.save()

        for feature_id in selected_features:
            feature = Feature.objects.get(id=feature_id)
            booking_request.features.add(feature)

        booking_request.save()

        messages.success(request, 'Auditorium booking requested successfully!')
        return redirect('user_index')

    context = {
        'auditorium': auditorium,
        'features': features,
        'date': date
    }
    return render(request, 'auditorium_details.html', context)

@login_required
def user_requests(request):
    requests = UserRequest.objects.filter(auditorium__user=request.user)
    context = {
        'requests': requests
    }
    return render(request, 'user_requests.html', context)

@login_required
def approve_request(request, request_id):
    user_request = get_object_or_404(UserRequest, id=request_id)

    # Check if the user is the owner of the auditorium
    if request.user != user_request.auditorium.user:
        return HttpResponseForbidden("You do not have permission to approve this request.")

    stripe.api_key = 'sk_test_51PYPLEEowOqVQOI5EO3xfdxlXeZumfYIelTtbrWLCdCsipg9l3E2BmQafQ5hstCRoogt9qXI8CJPGIgRswhNDnVd00alIj4ZC2'
    success_url = f"{request.scheme}://{request.get_host()}/success/"
    cancel_url = f"{request.scheme}://{request.get_host()}/cancel/"

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': user_request.auditorium.user.username,
                    },
                    'unit_amount': int(user_request.final_price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        user_request.stripe_payment_intent_id = session.id
        user_request.approved = True
        user_request.payment_requested = True
        user_request.save()

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    return redirect('user_requests')

@login_required
def reject_request(request, request_id):
    user_request = get_object_or_404(UserRequest, id=request_id)

    # Check if the user is the owner of the auditorium
    if request.user != user_request.auditorium.user:
        return HttpResponseForbidden("You do not have permission to reject this request.")

    user_request.delete()

    return redirect('user_requests')

@login_required
def user_messages(request):
    payment_requests = UserRequest.objects.filter(user=request.user, approved=True, payment_requested=True)
    context = {
        'payment_requests': payment_requests
    }
    return render(request, 'user_messages.html', context)

@login_required
def payment_form(request, request_id):
    print(f"Request ID: {request_id}")  # Debugging message
    try:
        user_request = UserRequest.objects.get(id=request_id)
        print(f"User Request found: {user_request}")  # Debugging message
    except UserRequest.DoesNotExist:
        print("User Request not found.")  # Debugging message
        messages.error(request, "User Request not found.")
        return redirect('user_messages')
    
    return render(request, 'payment_form.html', {'user_request': user_request})

@login_required
@csrf_exempt
def process_payment(request, request_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        card_number = request.POST.get('card_number')
        cvv = request.POST.get('cvv')

        # Validate card number and CVV
        if len(card_number) != 16 or not card_number.isdigit():
            messages.error(request, "Card number must be exactly 16 digits.")
            return redirect('payment_form', request_id=request_id)

        if len(cvv) != 3 or not cvv.isdigit():
            messages.error(request, "CVV must be exactly 3 digits.")
            return redirect('payment_form', request_id=request_id)

        try:
            # Retrieve the user request record
            user_request = UserRequest.objects.get(id=request_id)

            # Create a new entry in BookingHistory
            features_selected = ", ".join([feature.name for feature in user_request.features.all()])
            BookingHistory.objects.create(
                auditorium=user_request.auditorium,
                user=user_request.user,
                date_booked=user_request.date,
                features_selected=features_selected,
                final_price=user_request.final_price,
                card_number=card_number,
                cvv=cvv
            )

            # Create a new entry in Booking
            Booking.objects.create(
                auditorium=user_request.auditorium,
                user=user_request.user,
                date=user_request.date
            )

            # Optionally, delete the original user request entry if needed
            user_request.delete()

            return redirect('success')  # Replace 'success' with your success page name

        except UserRequest.DoesNotExist:
            messages.error(request, "User Request not found.")
            return redirect('user_messages')

    return redirect('user_messages')

@login_required
def cancel_payment(request, request_id):
    user_request = get_object_or_404(UserRequest, id=request_id)
    user_request.delete()
    messages.success(request, 'Payment request cancelled successfully.')
    return redirect('user_messages')

def success_page(request):
    return render(request, 'success.html')

@login_required
def event_my_bookings(request):
    try:
        # Assuming the user is associated with one auditorium
        auditorium = Auditorium.objects.get(user=request.user)
        bookings = BookingHistory.objects.filter(auditorium=auditorium)
    except Auditorium.DoesNotExist:
        bookings = []

    context = {
        'bookings': bookings,
        'auditorium': auditorium
    }
    return render(request, 'event_my_bookings.html', context)

@login_required
def user_my_bookings(request):
    # Fetch bookings related to the logged-in user
    bookings = BookingHistory.objects.filter(user=request.user)

    context = {
        'bookings': bookings
    }
    return render(request, 'user_my_bookings.html', context)
