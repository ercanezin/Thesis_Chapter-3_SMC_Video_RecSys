# Generated by Django 2.0.6 on 2018-07-10 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0012_auto_20180710_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_url',
            field=models.CharField(default='', max_length=100),
        ),
    ]
