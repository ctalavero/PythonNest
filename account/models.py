from django.contrib.auth import get_user_model
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

class Contact(models.Model):
    user_from = models.ForeignKey(User,related_name='rel_from_set',on_delete=models.CASCADE)
    user_to = models.ForeignKey(User,related_name='rel_to_set',on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'

user = get_user_model()
user.add_to_class('following',models.ManyToManyField('self',through=Contact,related_name='followers',symmetrical=False))