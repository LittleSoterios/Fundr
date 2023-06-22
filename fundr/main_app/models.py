from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=200)
    location = models.CharField(max_length=7, default="")
    latitude = models.FloatField(default=0.0, null=True)
    longitude = models.FloatField(default=0.0, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


    

class Fundraiser(models.Model):
    name = models.CharField(max_length = 100)
    bio  = models.CharField(max_length = 280)
    description = models.CharField(max_length = 1000)
    goal = models.FloatField(
        default=1000.0,
        validators=[
            MaxValueValidator(100000,0),
            MinValueValidator(10.0)
            ]
        )
    current = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0)
        ]
        )
    location = models.CharField(max_length=7,)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE) 
    # deletes all fundraisers when owners account is deleted // poses some opportunities for would-be scammers -- future implementation should have an archive database that holds details of fundraisers and their owners (beyond scope given timeframe)

    def __str__(self):
        return self.name
    
    

class Post(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    fundraiser = models.ForeignKey(Fundraiser, on_delete=models.CASCADE)
    image = models.URLField()
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=500)

    def __str__(self):
        return self.content
    



