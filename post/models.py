from django.db import models

from user.models import User


def user_directory_path(instance, filename):
    return 'user_{0}/resource/post_{1}/{2}'.format(instance.user_id, instance.id, filename)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)
    post_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    likes = models.IntegerField(default=0)
    available_level = models.IntegerField(default=0)
    resource = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    floor_num = models.IntegerField(default=1)

    def resource_path(self):
        if self.resource and hasattr(self.resource, 'url'):
            return self.resource.url
        else:
            return None

    def to_dict(self):
        return {
            'id': self.id,
            'user': User.objects.get(id=self.user_id).username,
            'type': self.type,
            'post_date': self.post_date,
            'title': self.title,
            'likes': self.likes,
            'available_level': self.available_level,
            'resource': self.resource_path(),
            'floor_num': self.floor_num
        }


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    floor = models.IntegerField()
    comment_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    likes = models.IntegerField(default=0)


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    browse_time = models.DateTimeField(auto_now_add=True)


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
