from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Auditorium, Feature, AuditoriumImage
import stripe
from django.forms import inlineformset_factory, modelformset_factory

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
