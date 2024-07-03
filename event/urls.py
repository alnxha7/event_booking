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

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('register_user/', views.register_user, name='register_user'),
    path('register_auditorium/', views.register_auditorium, name='register_auditorium'),
    path('user/', views.user_index, name='user_index'),
    path('host/', views.event_host_index, name='event_host_index'),
    path('user/bookings/', views.user_bookings, name='user_bookings'),
    path('host/schedules/', views.event_schedules, name='event_schedules'),
]