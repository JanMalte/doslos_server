from django.contrib.auth.models import AbstractUser
from django.db import models


class Word(models.Model):
    value = models.CharField(max_length=1000)
    level = models.ForeignKey('doslos.Level')


class Level(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    parent = models.ForeignKey('doslos.Level', blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=255)
    probability = models.IntegerField()
    next_category_threshold = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey('doslos.Category', blank=True, null=True)

    def __str__(self):
        return self.name


class WordProgress(models.Model):
    user = models.ForeignKey('doslos.User')
    word = models.ForeignKey('doslos.Word')
    category = models.ForeignKey('doslos.Category')
    right_answer_counter = models.IntegerField(default=0)


class User(AbstractUser):
    current_level = models.ForeignKey('doslos.Level', blank=True, null=True)
