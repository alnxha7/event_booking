# Generated by Django 4.2.3 on 2024-07-14 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auditorium', '0003_rename_username_auditorium_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditorium',
            name='capacity',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='auditorium',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='auditorium',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='auditorium',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auditorium.user'),
        ),
    ]
