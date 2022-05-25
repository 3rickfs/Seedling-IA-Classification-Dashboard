# Generated by Django 3.2.11 on 2022-05-25 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_auto_20220525_2050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='current_spa_session',
            name='spa_session_fdate',
        ),
        migrations.RemoveField(
            model_name='current_spa_session',
            name='spa_session_idate',
        ),
        migrations.AddField(
            model_name='seedling_process_analysis',
            name='spa_session_fdate',
            field=models.DateField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='seedling_process_analysis',
            name='spa_session_idate',
            field=models.DateField(editable=False, null=True),
        ),
    ]
