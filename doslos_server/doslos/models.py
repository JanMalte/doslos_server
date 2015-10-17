import random
from random import shuffle

from django.contrib.auth.models import AbstractUser
from django.db import models


class Word(models.Model):
    value = models.CharField(max_length=1000)
    level = models.ForeignKey('doslos.Level')

    def __str__(self):
        return self.value

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

    def __str__(self):
        return self.name

    def get_word_list(self, user):
        def get_words_for_level(level):
            words = []
            for word in level.word_set.all():
                for x in range(0, word.get_progress_for_user(user).category.probability):
                    words.append(word)
            return words

        words = get_words_for_level(self)
        level = self
        while level.parent is not None:
            level = level.parent
            words.extend(get_words_for_level(level))
        return words

    def get_random_word(self, user):
        word_list = self.get_word_list(user)
        return word_list[random.randint(0, len(word_list) - 1)]

    def get_possible_answers(self, word, user):
        answers = [word, ]
        word_list = set(self.get_word_list(user))
        while len(answers) < 4 and len(answers) != len(word_list):
            wrong_word = self.get_random_word(user)
            if wrong_word not in answers:
                answers.append(wrong_word)
        shuffle(answers)
        return answers


def get_default_level_id():
    return Level.objects.get_or_create(parent=None)[0].pk


class Category(models.Model):
    name = models.CharField(max_length=255)
    probability = models.IntegerField(default=0)
    next_category_threshold = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey('doslos.Category', blank=True, null=True)

    def __str__(self):
        return self.name


def get_default_category_id():
    return Category.objects.get_or_create(parent=None)[0].pk


class WordProgress(models.Model):
    user = models.ForeignKey('doslos.User')
    word = models.ForeignKey('doslos.Word', related_name='progress')
    category = models.ForeignKey('doslos.Category', default=get_default_category_id)
    right_answer_counter = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'word')


class User(AbstractUser):
    current_level = models.ForeignKey('doslos.Level', default=get_default_level_id)

    def __str__(self):
        return self.get_full_name()

    def get_available_levels(self):
        level = self.current_level
        levels = [level, ]
        while level.parent is not None:
            level = level.parent
            levels.append(level)
        return levels

    def complete_level(self, level):
        if level == self.current_level:
            self.current_level = Level.objects.get(parent=level)
