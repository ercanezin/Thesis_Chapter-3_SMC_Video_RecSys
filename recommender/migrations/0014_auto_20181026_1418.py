# Generated by Django 2.1.2 on 2018-10-26 14:18

from django.db import migrations
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0013_auto_20180710_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_myvideo',
            field=embed_video.fields.EmbedVideoField(blank=True, help_text='Copy vimeo url eg. "https://www.youtube.com/watch?v=tlLO7l9S-Rw"'),
        ),
    ]
