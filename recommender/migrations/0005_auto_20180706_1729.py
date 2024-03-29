# Generated by Django 2.0.6 on 2018-07-06 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0004_userinterests_userweigths'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='view_count',
            new_name='video_dislikes',
        ),
        migrations.RemoveField(
            model_name='video',
            name='video_id',
        ),
        migrations.AddField(
            model_name='video',
            name='video_description',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='video',
            name='video_duration',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='video',
            name='video_length',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='video',
            name='video_likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='video',
            name='video_rating',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='video',
            name='video_url',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='video',
            name='video_view_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='video',
            name='video_owner',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='video',
            name='video_title',
            field=models.CharField(default='', max_length=250),
        ),
    ]
