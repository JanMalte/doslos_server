from _csv import list_dialects
import csv
from doslos.models import Word, get_default_level, Level


def import_words_from_csv(csv_file):
    csv_reader = csv.reader(csv_file, delimiter=';')
    words = list()
    next(csv_reader) # skip first line
    words_in_level = 0
    current_level =get_default_level()
    for row in csv_reader:
        words_in_level += 1
        if words_in_level > 10:
            current_level = current_level.get_next_level()
            words_in_level = 1

        try:
            word = Word.objects.get(value_de=row[1])
        except Word.DoesNotExist:
            word = Word()

        word.value_de=row[1]
        word.value_en=row[2]
        word.level = current_level

        word.save()
        words.append(word)

    for old_word in Word.objects.exclude(pk__in=[word.pk for word in words]):
        old_word.delete()

    return words
