from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    date_of_birth = models.DateField(blank=True,null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d',blank=True,default='logos/default_user_logo.jpg')
    about = models.TextField(blank=True,null=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'

    def save(self, *args, **kwargs):
        if not self.photo:
            self.photo = 'logos/default_user_logo.jpg'
        super().save(*args, **kwargs)