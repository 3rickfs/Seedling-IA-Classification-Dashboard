# Generated by Django 3.2.11 on 2022-05-25 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_seedling_img_samples'),
    ]

    operations = [
        migrations.AddField(
            model_name='current_spa_session',
            name='spa_session_fdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='current_spa_session',
            name='spa_session_idate',
            field=models.DateField(blank=True, null=True),
        ),
    ]