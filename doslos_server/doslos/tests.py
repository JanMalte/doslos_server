from django.test import TestCase
from django_dynamic_fixture import G

from doslos.models import Word, User, WordProgress, Category, Level

"""
FIXME default values for foreign keys do not work with dynamic fixtures
"""


class WordTest(TestCase):
    def test_get_progress_for_user_default(self):
        user = G(User, current_level=G(Level))
        word = G(Word)
        self.assertEqual(0, word.get_progress_for_user(user).right_answer_counter)
        self.assertEqual(Category.objects.get_or_create(parent=None)[0], word.get_progress_for_user(user).category)

    def test_get_progress_for_user(self):
        user = G(User, current_level=G(Level))
        word = G(Word)
        progress = G(WordProgress, user=user, word=word, right_answer_counter=5, category=G(Category))
        self.assertEqual(progress, word.get_progress_for_user(user))

    def test_increase_right_answer_counter(self):
        user = G(User, current_level=G(Level))
        word = G(Word)
        word.increase_right_answer_counter(user)
        self.assertEqual(1, word.get_progress_for_user(user).right_answer_counter)

    def test_increase_right_answer_counter_reach_next_category(self):
        user = G(User, current_level=G(Level))
        word = G(Word)
        first_category = G(Category, next_category_threshold=5, parent=None)
        second_category = G(Category, next_category_threshold=10, parent=first_category)
        G(WordProgress, user=user, word=word, right_answer_counter=4, category=first_category)
        word.increase_right_answer_counter(user)
        self.assertEqual(5, word.get_progress_for_user(user).right_answer_counter)
        self.assertEqual(second_category, word.get_progress_for_user(user).category)

    def test_reset_right_answer_counter(self):
        user = G(User, current_level=G(Level))
        word = G(Word)
        word.reset_right_answer_counter(user)
        self.assertEqual(0, word.get_progress_for_user(user).right_answer_counter)
        self.assertEqual(Category.objects.get_or_create(parent=None)[0], word.get_progress_for_user(user).category)

    def test_reset_right_answer_counter_existing_progress(self):
        user = G(User, current_level=G(Level))
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
        user = G(User, current_level=first_level)
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


class LevelTest(TestCase):
    user = None

    @property
    def level(self):
        return self.user.current_level

    def setUp(self):
        self.user = G(User, current_level=G(Level))

    def test_get_word_list_no_words(self):
        G(Category, parent=None, probability=1)
        self.assertEqual(0, len(self.level.get_word_list(self.user)))

    def test_get_word_list_only_one_word(self):
        G(Category, parent=None, probability=1)
        word = G(Word, level=self.user.current_level)
        word_list = self.level.get_word_list(self.user)
        self.assertIn(word, word_list)
        self.assertEqual(1, len(word_list))

    def test_get_word_list_only_one_word_with_probability(self):
        G(Category, parent=None, probability=10)
        word = G(Word, level=self.user.current_level)
        word_list = self.level.get_word_list(self.user)
        self.assertIn(word, word_list)
        self.assertEqual(10, len(word_list))

    def test_get_word_list_two_words(self):
        G(Category, parent=None, probability=1)
        first_word = G(Word, level=self.user.current_level)
        second_word = G(Word, level=self.user.current_level)
        word_list = self.level.get_word_list(self.user)
        self.assertIn(first_word, word_list)
        self.assertIn(second_word, word_list)
        self.assertEqual(2, len(word_list))

    def test_get_word_list_only_one_word_with_probability(self):
        G(Category, parent=None, probability=10)
        first_word = G(Word, level=self.user.current_level)
        second_word = G(Word, level=self.user.current_level)
        word_list = self.level.get_word_list(self.user)
        self.assertIn(first_word, word_list)
        self.assertIn(second_word, word_list)
        self.assertEqual(20, len(word_list))

    def test_get_word_list_only_one_word_with_different_probabilities(self):
        first_category = G(Category, parent=None, probability=10)
        second_category = G(Category, parent=first_category, probability=5)
        first_word = G(Word, level=self.user.current_level)
        second_word = G(Word, level=self.user.current_level)
        G(WordProgress, user=self.user, word=first_word, category=first_category)
        G(WordProgress, user=self.user, word=second_word, category=second_category)
        word_list = self.level.get_word_list(self.user)
        self.assertIn(first_word, word_list)
        self.assertIn(second_word, word_list)
        self.assertEqual(15, len(word_list))
        self.assertEqual(10, word_list.count(first_word))
        self.assertEqual(5, word_list.count(second_word))
