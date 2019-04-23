# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponseRedirect
from django.http import QueryDict
from django.db import transaction
from .models import Form, Course, Subject, Option, Result

def get_order_response(form):
    r = Result.objects.filter(form=form)
    if r:
        return max(r, key=lambda x:x.order).order + 1
    else:
        return 1

class Object(object):
    pass

def obtem_parametros_para_filtro(request):
	r = request.get_full_path()
	if '?' in r:
		return r.split('?')[-1]
	return ''

def obtem_query(request):
    filtro = obtem_parametros_para_filtro(request)
    return QueryDict(filtro, mutable = True)

def subjects(request, form_public_id, course_code=None):
    query = obtem_query(request)
    form = Form.objects.get(public_id=form_public_id)
    if course_code is None:
        raise "erro"
    course = Course.objects.get(code=course_code)
    if 'subjects' in query:
        ids = list(map(int, query.get('subjects').split(',')))
        subjects = Subject.objects.select_related().filter(pk__in=ids)
        if request.method == 'POST':
            with transaction.atomic():
                data = dict(request.POST)
                order = get_order_response(form)
                for subject in subjects:
                    for group in form.groups.all():
                        for question in group.questions.all():

                            if question.type == 'text':
                                option = None
                                answer = data.get(question.public_id + '_by_' + str(subject.id))[0]
                            if question.type in ['range', 'number']:
                                option = None
                                answer = data.get(question.public_id + '_by_' + str(subject.id))[0]

                            elif question.type in ['radio', 'select']:
                                answer = data.get(question.public_id + '_by_' + str(subject.id))[0]
                                if answer is None:
                                    return render(request, 'subjects.html',
                                        {
                                            'subjects': subjects,
                                            'form': form,
                                            'course': course,
                                            'error': 'Você tentou enviar uma resposta faltando informações. Por favor, tente novamente!'
                                    })
                                option = Option.objects.get(id=answer)
                            Result.objects.create(
                                order=order,
                                question=question,
                                form=form,
                                answer=answer,
                                subject=subject
                            )
                return render(request, 'subjects.html',
                    {


                        'success': 'Obrigado por contribuir com este formulário!'
                })





                keys = [e for e in a.keys() if '_by_' in e]
                keys = sorted(keys, key=lambda x: x.split('_by_')[1])
                print(*keys, sep='\n')
        return render(request, 'subjects.html',
            {
                'subjects': subjects,
                'form': form,
                'course': course
        })


    if request.method == 'POST':
        print(request.POST)
        a = dict(request.POST)
        print(a)
        a = ','.join(a['subjects'])
        print(a)
        return HttpResponseRedirect('?subjects=' + a)
    subjects = Subject.objects.select_related().filter(course__code=course_code, eletiva=False)
    eletivas = Subject.objects.select_related().filter(eletiva=True)
    grades = []
    for p in range(1, 11):
        o = Object()
        o.eletiva = False
        o.number = p
        o.subjects = subjects.filter(grade=p)
        grades.append(o)
    o = Object()
    o.eletiva = True
    o.subjects = eletivas
    grades.append(o)

    return render(request, 'subjects.html',
        {
            'grades': grades,
            'form': form,
            'course': course
    })
