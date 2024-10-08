# Generated by Django 4.2.3 on 2024-07-21 17:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auditorium', '0008_bookinghistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_booked', models.DateField()),
                ('date_of_booking', models.DateTimeField(auto_now_add=True)),
                ('features_selected', models.TextField()),
                ('final_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('card_number', models.CharField(max_length=16)),
                ('cvv', models.CharField(max_length=4)),
                ('auditorium', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auditorium.auditorium')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
