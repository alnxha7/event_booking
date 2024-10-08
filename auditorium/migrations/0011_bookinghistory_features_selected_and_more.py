# Generated by Django 4.2.3 on 2024-07-21 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditorium', '0010_delete_bookingdetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookinghistory',
            name='features_selected',
            field=models.TextField(default='No features selected'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bookinghistory',
            name='final_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
