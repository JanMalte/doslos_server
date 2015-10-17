from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from doslos.models import Word, Level


def select_level(request):
    return render(request, 'doslos/select_level.html',
                  context={'available_levels': request.user.get_available_levels()})


def questionnaire(request, level_id):
    level = Level.objects.get(pk=level_id)
    word = level.get_random_word(request.user)
    answers = level.get_possible_answers(word, request.user)
    context = {
        'level_id': level_id,
        'level': level,
        'word': word,
        'answers': answers,
        'level_right_answer_counter': request.session.get('level_right_answer_counter', 0),
        'completed_percentage': request.session.get('level_right_answer_counter', 0) / 10 * 100
    }
    return render(request, 'doslos/questionnaire.html', context=context)


def post_questionnaire(request, level_id):
    level = Level.objects.get(pk=level_id)
    level_right_answer_counter = request.session.get('level_right_answer_counter', 0)
    try:
        word = Word.objects.get(pk=request.POST.get('word_id', 0))
        if word.value_de == request.POST.get('answer', ''):
            level_right_answer_counter += 1
            word.increase_right_answer_counter(request.user)
            messages.success(request, _('The answer was correct'))
        else:
            level_right_answer_counter = 0
            word.reset_right_answer_counter(request.user)
            messages.warning(request, _('The answer was not correct. The correct answer is "%s"') % word.value_de)
        if level_right_answer_counter >= 10:
            request.user.complete_level(level)
            level_right_answer_counter = 0
            request.session['level_right_answer_counter'] = level_right_answer_counter
            messages.success(request, _('You completed the level "%s"') % level.name)
            return redirect(reverse('select_level'))
        request.session['level_right_answer_counter'] = level_right_answer_counter
    except Word.DoesNotExist:
        pass
    return redirect(reverse('questionnaire', kwargs={'level_id': int(level_id)}))
