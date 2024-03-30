from django.contrib.auth.models import User
from django.db import models
from embed_video.fields import EmbedVideoField


class Bundle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, default='')
    end_date = models.DateTimeField()
    number_of_final_dest = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name + ' - ' + self.user.username


class POI(models.Model):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, null=True)
    location_name = models.CharField(max_length=200, default='')
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.bundle.name + ' - ' + self.location_name


class Video(models.Model):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, null=True)
    poi = models.ForeignKey(POI, on_delete=models.CASCADE, null=True)
    video_url = models.CharField(max_length=100, default='')
    video_title = models.TextField(default='')
    video_owner = models.TextField(default='')
    video_view_count = models.IntegerField(default=0)
    video_length = models.IntegerField(default=0)
    video_description = models.TextField(default='')
    video_rating = models.FloatField(default=0.0)
    video_likes = models.IntegerField(default=0)
    video_dislikes = models.IntegerField(default=0)
    video_duration = models.CharField(max_length=20, default='')
    video_myvideo = EmbedVideoField(blank=True,
                                    help_text='Copy youtube url eg.')
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.video_url + ' - ' + self.video_title


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.user.username + ' - ' + self.bundle.name


class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True)
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, null=True)
    is_liked = models.SmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.user.username + ' - ' + self.video.video_title + ' - ' + self.video.video_url


class RecListItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="person2persons")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True)
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, null=True)
    is_trust = models.BooleanField(default=False)
    trust_list_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="trustee")
    is_liked = models.SmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    proportion = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
