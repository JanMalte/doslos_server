from django.contrib.auth.models import AbstractUser
from django.db import models


class Word(models.Model):
    value = models.CharField(max_length=1000)
    level = models.ForeignKey('doslos.Level')

    def get_progress_for_user(self, user):
        return WordProgress.objects.get_or_create(user=user, word=self)[0]

    def increase_right_answer_counter(self, user):
        progress = self.get_progress_for_user(user)
        progress.right_answer_counter += 1
        if progress.category.next_category_threshold and (
                progress.right_answer_counter >= progress.category.next_category_threshold):
            progress.category = Category.objects.get(parent=progress.category)
        progress.save()

    def reset_right_answer_counter(self, user):
        progress = self.get_progress_for_user(user)
        progress.right_answer_counter = 0
        progress.category = Category.objects.get_or_create(parent=None)[0]
        progress.save()


class Level(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    parent = models.ForeignKey('doslos.Level', blank=True, null=True)

    def get_random_word(self, user):
        raise NotImplementedError('Not implemented')

    def get_possible_answers(self, word, user):
        raise NotImplementedError('Not implemented')


class Category(models.Model):
    name = models.CharField(max_length=255)
    probability = models.IntegerField(default=0)
    next_category_threshold = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey('doslos.Category', blank=True, null=True)

    def __str__(self):
        return self.name


class WordProgress(models.Model):
    user = models.ForeignKey('doslos.User')
    word = models.ForeignKey('doslos.Word', related_name='progress')
    category = models.ForeignKey('doslos.Category', default=lambda: Category.objects.get_or_create(parent=None)[0])
    right_answer_counter = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'word')


class User(AbstractUser):
    current_level = models.ForeignKey('doslos.Level', blank=True, null=True)

    def get_available_levels(self):
        raise NotImplementedError('Not implemented')

    def complete_level(self, level):
        raise NotImplementedError('Not implemented')
