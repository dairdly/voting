from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models 
from django.utils import timezone

from datetime import datetime


class CustomAccountManager(BaseUserManager):

    def _create_user(self, username, password, **other_fields):
        """create and saves the user with the given info"""

        if not username:
            raise ValueError(('You must provide a username'))

        user = self.model(username=username, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **other_fields):
        other_fields.setdefault('is_superuser', False)
        other_fields.setdefault('is_staff', False)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('hasVoted', False)

        return self._create_user(username, password, **other_fields)

    def create_superuser(self, username, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('hasVoted', False)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self._create_user(username, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    
    username = models.CharField(max_length=20, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    hasVoted = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username}"


class Candidate(models.Model):

    class Meta:
        get_latest_by = "votes"
        ordering = ["votes", "level"]
        default_related_name = "aspirant"

    class Levels(models.IntegerChoices):
        one = 100
        two = 200 
        three = 300 
        four = 400 
        five = 500

    name = models.CharField(max_length=30, unique=True)
    level = models.IntegerField(choices=Levels.choices)
    votes = models.IntegerField(default=0)
    post = models.ForeignKey('main.Position', on_delete=models.SET_NULL, null=True)
    election = models.ForeignKey('main.Election', on_delete=models.CASCADE, related_name='candidates')

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=30, unique=True)
    candidates = models.ManyToManyField(Candidate)
    election = models.ForeignKey('main.Election', on_delete=models.CASCADE, null=True, related_name='positions')
    
    def __str__(self):
        return self.name 


class Election(models.Model):
    name = models.CharField(max_length=20)
    start = models.DateTimeField()
    end = models.DateTimeField()
    started = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if datetime.now(timezone.utc) >= self.start:
            self.started = True
        if datetime.now(timezone.utc) >= self.end:
            self.ended = True
        return super().save(*args, **kwargs)