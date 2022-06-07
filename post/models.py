from django.db import models

from user.models import User


class Resource(models.Model):
    resource_name = models.CharField(max_length=50)
    resource_path = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)
    post_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    likes = models.IntegerField(default=0)
    available_level = models.IntegerField(default=0)
    resource_id = models.ForeignKey(Resource, on_delete=models.SET_NULL, blank=True, null=True)
    floor_num = models.IntegerField(default=1)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    floor = models.IntegerField()
    comment_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    likes = models.IntegerField(default=0)

