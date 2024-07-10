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
    path('user_bookings/', views.user_bookings, name='user_bookings'),
    path('host_schedules/', views.event_schedules, name='event_schedules'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)