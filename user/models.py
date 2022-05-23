from django.db import models

# Create your models here.


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
    # headshot = models.ImageField()
    security_issue = models.CharField(max_length=255, default="密保问题")
    security_answer = models.CharField(max_length=255, default="密保答案")
