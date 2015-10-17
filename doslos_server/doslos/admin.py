from django.contrib import admin

from doslos.models import WordProgress, Word, User, Category, Level

admin.site.register(Word)
admin.site.register(Level)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(WordProgress)