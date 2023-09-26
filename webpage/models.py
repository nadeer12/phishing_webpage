from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class blacklist(models.Model):
    no=models.IntegerField()
    url_name=models.CharField(max_length=2500)

class Message(models.Model):
    user_name=models.CharField(max_length=200, null=False ,blank=False)
    user_email=models.CharField(max_length=200, null=False ,blank=False)
    user_message=models.TextField()

class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
def __str__(self):
    return self.user.username
