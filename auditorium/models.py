from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.conf import settings
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return self.is_superuser or super().has_module_perms(app_label)

class Auditorium(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    capacity = models.IntegerField()
    features = models.ManyToManyField('Feature', related_name='auditoriums', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to='auditorium_images/', blank=True, default='../static/images/blue_mac2.jpg')
    approved = models.BooleanField(default=False)  # Ensure this field exists

class Feature(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    auditorium = models.ForeignKey(Auditorium, related_name='auditorium_features', on_delete=models.CASCADE)

class AuditoriumImage(models.Model):
    auditorium = models.ForeignKey(Auditorium, related_name='auditorium_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='auditorium_images/')

class Booking(models.Model):
    auditorium = models.ForeignKey('Auditorium', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    booked_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.auditorium} booked by {self.user} on {self.date}'

    
class UserRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    date = models.DateField()
    features = models.ManyToManyField(Feature)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    approved = models.BooleanField(default=False)
    payment_requested = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BookingHistory(models.Model):
    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_booked = models.DateField()
    date_of_booking = models.DateTimeField(auto_now_add=True)
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.user.username} - {self.auditorium.user.username} - {self.date_booked}"