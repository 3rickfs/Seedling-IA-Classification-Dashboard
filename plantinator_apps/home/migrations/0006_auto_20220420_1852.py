# Generated by Django 3.2.11 on 2022-04-20 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_auto_20220420_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seedling_process_analysis',
            name='avrg_seedling_quality_prcntg',
            field=models.FloatField(default=0.0, editable=False),
        ),
        migrations.AlterField(
            model_name='seedling_process_analysis',
            name='avrg_seedling_quality_qty',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='seedling_process_analysis',
            name='bad_seedling_quality_prcntg',
            field=models.FloatField(default=0.0, editable=False),
        ),
        migrations.AlterField(
            model_name='seedling_process_analysis',
            name='bad_seedling_quality_qty',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='seedling_process_analysis',
            name='good_seedling_quality_prcntg',
            field=models.FloatField(default=0.0, editable=False),
        ),
        migrations.AlterField(
            model_name='seedling_process_analysis',
            name='good_seedling_quality_qty',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='seedling_process_analysis',
            name='tot_artichokes_seedlng_imgs',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
