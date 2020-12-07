from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profile_pics")

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def clean(self, *args, **kwargs):        
        return super().clean(*args, **kwargs)

class Post(models.Model):
    title=models.CharField(max_length=100)
    imageURL= models.ImageField()
    content= models.TextField()
    subtitle= models.CharField(max_length=100)
    published_at=models.DateField()
    author=models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}'

class Comments(models.Model):
    content = models.TextField()
    created_at = models.DateField()
    active = models.BooleanField()
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
