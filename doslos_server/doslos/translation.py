from modeltranslation.translator import translator, TranslationOptions

from .models import Level, Word


class WordTranslationOptions(TranslationOptions):
    fields = ('value',)


class LevelTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


translator.register(Word, WordTranslationOptions)
translator.register(Level, LevelTranslationOptions)
