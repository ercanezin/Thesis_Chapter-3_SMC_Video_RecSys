# Generated by Django 2.1.2 on 2018-11-13 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0023_auto_20181109_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='bundle',
            name='number_of_final_dest',
            field=models.IntegerField(default=0),
        ),
    ]
