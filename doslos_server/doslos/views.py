from django.shortcuts import render, redirect

from doslos.models import Word, Level


def select_level(request):
    return render(request, 'doslos/select_level.html',
                  context={'available_levels': request.user.get_available_levels()})


def questionnaire(request, level_id):
    level = Level.objects.get(pk=level_id)
    word = level.get_random_word(request.user)
    answers = level.get_answers(word, request.user)
    context = {
        'level_id': level_id,
        'word': word,
        'answers': answers,
        'level_right_answer_counter': request.session.get('level_right_answer_counter', 0)
    }
    return render(request, 'doslos/questionnaire.html', context=context)


def post_questionnaire(request, level_id):
    level = Level.objects.get(pk=level_id)
    level_right_answer_counter = request.session.get('level_right_answer_counter', 0)
    word = Word.objects.get(pk=request.POST['word_id'])
    if word.value_de == request.POST['answer']:
        level_right_answer_counter += 1
        word.increase_right_answer_counter(request.user)
    else:
        level_right_answer_counter = 0
        word.reset_right_answer_counter(request.user)
    if level_right_answer_counter >= 10:
        request.user.complete_level(level)
        level_right_answer_counter = 0
        request.session['level_right_answer_counter'] = level_right_answer_counter
        return redirect('select_level')
    request.session['level_right_answer_counter'] = level_right_answer_counter
    return redirect('questionaire')
