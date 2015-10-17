from django.test import TestCase
from django_dynamic_fixture import G, F

from doslos.models import Word, User, WordProgress, Category, Level


class WordTest(TestCase):
    def test_get_progress_for_user_default(self):
        user = G(User)
        word = G(Word)
        self.assertEqual(0, word.get_progress_for_user(user).right_answer_counter)
        self.assertEqual(Category.objects.get_or_create(parent=None)[0], word.get_progress_for_user(user).category)

    def test_get_progress_for_user(self):
        user = G(User)
        word = G(Word)
        progress = G(WordProgress, user=user, word=word, right_answer_counter=5)
        self.assertEqual(progress, word.get_progress_for_user(user))

    def test_increase_right_answer_counter(self):
        user = G(User)
        word = G(Word)
        word.increase_right_answer_counter(user)
        self.assertEqual(1, word.get_progress_for_user(user).right_answer_counter)

    def test_increase_right_answer_counter_reach_next_category(self):
        user = G(User)
        word = G(Word)
        first_category = G(Category, next_category_threshold=5, parent=None)
        second_category = G(Category, next_category_threshold=10, parent=first_category)
        G(WordProgress, user=user, word=word, right_answer_counter=4, category=first_category)
        word.increase_right_answer_counter(user)
        self.assertEqual(5, word.get_progress_for_user(user).right_answer_counter)
        self.assertEqual(second_category, word.get_progress_for_user(user).category)

    def test_reset_right_answer_counter(self):
        user = G(User)
        word = G(Word)
        word.reset_right_answer_counter(user)
        self.assertEqual(0, word.get_progress_for_user(user).right_answer_counter)
        self.assertEqual(Category.objects.get_or_create(parent=None)[0], word.get_progress_for_user(user).category)

    def test_reset_right_answer_counter_existing_progress(self):
        user = G(User)
        word = G(Word)
        second_category = G(Category, next_category_threshold=5, parent=G(Category))
        G(WordProgress, user=user, word=word, right_answer_counter=4, category=second_category)
        word.reset_right_answer_counter(user)
        self.assertEqual(0, word.get_progress_for_user(user).right_answer_counter)
        self.assertEqual(Category.objects.get_or_create(parent=None)[0], word.get_progress_for_user(user).category)


class UserTest(TestCase):
    def test_get_available_levels(self):
        level = G(Level)
        user = G(User, current_level=level)
        self.assertIn(level, user.get_available_levels())

    def test_get_available_levels_recursive(self):
        first_level = G(Level)
        second_level = G(Level, parent=first_level)
        user = G(User, current_level=second_level)
        self.assertIn(first_level, user.get_available_levels())
        self.assertIn(second_level, user.get_available_levels())

    def test_get_available_levels_recursive_only_first_level_reached(self):
        first_level = G(Level)
        second_level = G(Level, parent=first_level)
        user = G(User, current_level=first_level)
        self.assertIn(first_level, user.get_available_levels())
        self.assertNotIn(second_level, user.get_available_levels())

    def test_current_level_is_first_level_by_defaut(self):
        first_level = G(Level, parent=None)
        user = G(User)
        self.assertEqual(first_level, user.current_level)

    def test_complete_first_level(self):
        first_level = G(Level)
        second_level = G(Level, parent=first_level)
        user = G(User, current_level=first_level)
        user.complete_level(first_level)
        self.assertEqual(second_level, user.current_level)

    def test_complete_first_level_again(self):
        first_level = G(Level)
        second_level = G(Level, parent=first_level)
        third_level = G(Level, parent=second_level)
        user = G(User, current_level=third_level)
        user.complete_level(first_level)
        self.assertEqual(third_level, user.current_level)
