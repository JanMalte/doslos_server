from unittest.mock import patch
from _pyio import StringIO

from django.test import TestCase
from django_dynamic_fixture import G

from doslos.models import Word, User, WordProgress, Category, Level
from doslos.import_data  import import_words_from_csv

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

    def test_complete_last_level(self):
        first_level = G(Level)
        second_level = G(Level, parent=first_level)
        user = G(User, current_level=second_level)
        user.complete_level(second_level)
        self.assertEqual(second_level, user.current_level)


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

    def test_get_word_list_only_one_word_with_different_probabilities_in_different_levels_second_not_reached(self):
        first_level = self.level
        second_level = G(Level)
        first_category = G(Category, parent=None, probability=10)
        second_category = G(Category, parent=first_category, probability=5)
        first_word = G(Word, level=first_level)
        second_word = G(Word, level=second_level)
        G(WordProgress, user=self.user, word=first_word, category=first_category)
        G(WordProgress, user=self.user, word=second_word, category=second_category)
        word_list = self.level.get_word_list(self.user)
        self.assertIn(first_word, word_list)
        self.assertNotIn(second_word, word_list)
        self.assertEqual(10, len(word_list))
        self.assertEqual(10, word_list.count(first_word))

    def test_get_word_list_only_one_word_with_different_probabilities_in_different_levels_second_reached(self):
        first_level = self.level
        second_level = G(Level, parent=first_level)
        first_category = G(Category, parent=None, probability=10)
        second_category = G(Category, parent=first_category, probability=5)
        first_word = G(Word, level=first_level)
        second_word = G(Word, level=second_level)
        G(WordProgress, user=self.user, word=first_word, category=first_category)
        G(WordProgress, user=self.user, word=second_word, category=second_category)
        self.user.current_level = second_level
        self.user.save()
        word_list = second_level.get_word_list(self.user)
        self.assertIn(first_word, word_list)
        self.assertIn(second_word, word_list)
        self.assertEqual(15, len(word_list))
        self.assertEqual(10, word_list.count(first_word))
        self.assertEqual(5, word_list.count(second_word))


@patch('random.randint', return_value=2)
class GetRandomWordTest(TestCase):
    def test_get_random_word(self, mocked_randint):
        from .models import Level as PatchedLevel

        expected_word = G(Word)

        def get_word_list(user):
            return [G(Word), G(Word), expected_word, G(Word), G(Word)]

        level = PatchedLevel()
        level.get_word_list = get_word_list
        word = level.get_random_word(User())
        self.assertEqual(expected_word, word)
        mocked_randint.assert_called_with(0, 4)


class GetPossibleAnswersTest(TestCase):
    def test_get_possible_answers(self):
        level = G(Level, parent=None)
        word = G(Word, level=level)
        word_list = [G(Word, level=level), G(Word, level=level), G(Word, level=level), word]

        def get_word_list(user=None):
            return word_list

        level.get_word_list = get_word_list
        answers = level.get_possible_answers(word, User())
        self.assertSetEqual(set(get_word_list()), set(answers))

    def test_get_possible_answers_not_enough_words(self):
        level = G(Level, parent=None)
        word = G(Word, level=level)
        word_list = [G(Word, level=level), word]

        def get_word_list(user=None):
            return word_list

        level.get_word_list = get_word_list
        answers = level.get_possible_answers(word, User())
        self.assertSetEqual(set(get_word_list()), set(answers))


class ImportTest(TestCase):

    def test_first_line_is_ignored(self):
        words = import_words_from_csv(StringIO(';a;b\nignored;original;translation'))
        self.assertEqual(1, len(words))

    def test_one_word(self):
        words = import_words_from_csv(StringIO(';a;b\nignored;germanword;englishword'))
        self.assertEqual('germanword', words[0].value_de)
        self.assertEqual('englishword', words[0].value_en, )

    def test_another_word(self):
        words = import_words_from_csv(StringIO(';a;b\nignored;grün;green'))
        self.assertEqual('grün', words[0].value_de)
        self.assertEqual('green', words[0].value_en)

    def test_two_words(self):
        words = import_words_from_csv(StringIO(';a;b\nignored;grün;green\nignored;Auto;car'))
        self.assertEqual('grün', words[0].value_de)
        self.assertEqual('green', words[0].value_en)
        self.assertEqual('Auto', words[1].value_de)
        self.assertEqual('car', words[1].value_en)

    def test_word_is_saved_in_db(self):
        import_words_from_csv(StringIO(';a;b\nignored;grün;green\nignored;Auto;car'))
        words = Word.objects.all()
        self.assertEqual('grün', words[0].value_de)
        self.assertEqual('green', words[0].value_en)
        self.assertEqual('Auto', words[1].value_de)
        self.assertEqual('car', words[1].value_en)

    def test_word_are_divided_into_levels(self):
        level1 = G(Level, parent=None)
        level2 = G(Level, parent=level1)
        level3 = G(Level, parent=level2)
        csv = ';;'

        for i in range(0,21):
            csv += '\nignored;w' + str(i) + ';t' + str(i)
        import_words_from_csv(StringIO(csv))
        words = Word.objects.all()
        for i in range(1,9):
            self.assertEqual(words[i].level, level1)
            self.assertEqual('w' + str(i), words[i].value_de)
            self.assertEqual('t' + str(i), words[i].value_en)
        for i in range(10,19):
            self.assertEqual(words[i].level, level2)
            self.assertEqual('w' + str(i), words[i].value_de)
            self.assertEqual('t' + str(i), words[i].value_en)
        for i in range(20,21):
            self.assertEqual(words[i].level, level3)
            self.assertEqual('w' + str(i), words[i].value_de)
            self.assertEqual('t' + str(i), words[i].value_en)

    def test_existing_word_is_removed(self):
        old_word = G(Word, value_de='alt', value_en='old')
        old_word_id = old_word.pk
        import_words_from_csv(StringIO(';;\nignored;grün;green'))
        self.assertEqual(0, len(Word.objects.filter(pk=old_word_id)))

    def test_existing_word_is_updated_id_german_is_the_same(self):
        old_word = G(Word, value_de='alt', value_en='wrongenglish')
        old_word_id = old_word.pk
        import_words_from_csv(StringIO(';;\nignored;alt;old'))
        new_word = Word.objects.get(pk=old_word_id)
        self.assertEqual(old_word_id, new_word.pk)
        self.assertEqual('alt', new_word.value_de)
        self.assertEqual('old', new_word.value_en)
        self.assertEqual(1, len(Word.objects.all()))

    def test_existing_word_change_level(self):
        level1 = G(Level, parent=None)
        level2 = G(Level, parent=level1)
        level3 = G(Level, parent=level2)
        old_word = G(Word, value_de='alt', value_en='wrongenglish', level = level2)
        old_word_id = old_word.pk
        import_words_from_csv(StringIO(';;\nignored;alt;old'))
        new_word = Word.objects.get(pk=old_word_id)
        self.assertEqual(level1, new_word.level)
