# Generated by Django 4.2.3 on 2024-07-22 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditorium', '0011_bookinghistory_features_selected_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookinghistory',
            name='admin_amount',
            field=models.DecimalField(decimal_places=2, default=2000, editable=False, max_digits=10),
            preserve_default=False,
        ),
    ]
