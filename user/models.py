from django.db import models

# Create your models here.

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = 'headshot.' + ext
    return 'user_{0}/headshot/{1}'.format(instance.id, filename)


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    description = models.TextField(default='')
    sex = models.BooleanField(null=True)
    grade = models.IntegerField(null=True)
    major = models.CharField(max_length=20)
    level = models.IntegerField(default=1)
    blockTime = models.IntegerField(default=0)
    first_login = models.BooleanField(default=True)
    headshot = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    security_issue = models.CharField(max_length=255, default="密保问题")
    security_answer = models.CharField(max_length=255, default="密保答案")

    def photo_url(self):
        if self.headshot and hasattr(self.headshot, 'url'):
            return self.headshot.url
        else:
            return '/media/default/user.jpeg'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'description': self.description,
            'grade': self.grade,
            'major': self.major,
            'sex': self.sex,
            'headshot': self.photo_url()
        }
