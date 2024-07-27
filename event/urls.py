"""
URL configuration for event project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from auditorium import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('register_user/', views.register_user, name='register_user'),
    path('register_auditorium/', views.register_auditorium, name='register_auditorium'),
    path('user/', views.user_index, name='user_index'),
    path('host/', views.event_host_index, name='event_host_index'),

    path('event_features/<int:auditorium_id>/', views.event_features, name='event_features'),
    path('user_bookings/', views.user_bookings, name='user_bookings'),
    path('host_schedules/<int:auditorium_id>/', views.event_schedules, name='event_schedules'),
    path('manage-booking/<int:auditorium_id>/', views.manage_booking, name='manage_booking'),
    path('auditorium_list/<int:auditorium_id>/', views.auditorium_list, name='auditorium_list'),
    path('user_slot', views.user_event_schedules, name='user_event_schedules'),
    path('book_calendar/<int:auditorium_id>/', views.book_calendar, name='book_calendar'),
    path('auditorium/<int:auditorium_id>/details/', views.auditorium_details, name='auditorium_details'),
    path('user_requests/', views.user_requests, name='user_requests'),
    path('view_requests/', views.view_requests, name='view_requests'),
    
    path('messages/', views.user_messages, name='user_messages'),
    path('approve_request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),

    path('user/messages/', views.user_messages, name='user_messages'),
    path('payment_form/<int:request_id>/', views.payment_form, name='payment_form'),
    path('process_payment/<int:request_id>/', views.process_payment, name='process_payment'),
    path('cancel_payment/<int:request_id>/', views.cancel_payment, name='cancel_payment'),
    path('success/', views.success_page, name='success'),

    path('event_my_bookings/', views.event_my_bookings, name='event_my_bookings'),
    path('user_my_bookings/', views.user_my_bookings, name='user_my_bookings'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)