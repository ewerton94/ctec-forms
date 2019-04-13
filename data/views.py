# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponseRedirect
from django.http import QueryDict
from .models import Form, Course, Subject


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
        subjects = Subject.objects.filter(pk__in=ids)
        if request.method == 'POST':
            print(request.POST)
            a = dict(request.POST)
            print(a)
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
