# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
import string
from django.db import models

def rand_slug(n):
    return ''.join(random.choice(string.ascii_letters) for _ in range(n))

QUESTION_TYPES = (
    ('radio', 'Múltipla escolha (radio)'),
    ('select', 'Múltipla escolha (dropdown)'),
    ('text', 'Aberta (texto)'),
    ('number', 'Aberta (número)'),
    ('range', 'Escala de 1 a 10'),
)

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=4)
    def __str__(self):
        return self.name

class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    course = models.ForeignKey(Course)
    eletiva = models.BooleanField()
    grade = models.IntegerField()

    def __str__(self):
        return self.name

class Option(models.Model):
    class Meta:
        ordering = ['id',]
        verbose_name = 'Opção'
        verbose_name_plural = 'Opções'
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Question(models.Model):
    class Meta:
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'
        ordering = ['id',]
    public_id = models.CharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=1000)
    type = models.CharField(max_length=100, choices=QUESTION_TYPES)
    options = models.ManyToManyField(Option, related_name='questions', blank=True)
    def save(self, **kwargs):
        if not self.public_id:
            while True:
                public_id = rand_slug(15)
                find = Question.objects.filter(public_id=public_id)
                if not find:
                    self.public_id = public_id
                    break
        super(Question, self).save(**kwargs)

        def __str__(self):
            return self.name

class Group(models.Model):
    class Meta:
        pass
    name = models.CharField(max_length=1000)
    questions = models.ManyToManyField(Question, related_name='groups', blank=True)

class Form(models.Model):
    class Meta:
        verbose_name = 'Formulário'
        verbose_name_plural = 'Formulários'
        ordering = ['id',]
    description = models.TextField(default='')
    public_id = models.CharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=1000)
    groups = models.ManyToManyField(Group, related_name='forms', blank=True)
    situation = models.BooleanField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def is_editable(self):
        results = Result.objects.filter(form=self.id)
        return False if results else True

    def save(self, **kwargs):
        if not self.public_id:
            while True:
                public_id = rand_slug(15)
                find = Form.objects.filter(public_id=public_id)
                if not find:
                    self.public_id = public_id
                    break
        super(Form, self).save(**kwargs)

        def __str__(self):
            return self.name


class Result(models.Model):
    class Meta:
        verbose_name = 'Resultado'
        verbose_name_plural = 'Resultados'
    order = models.IntegerField()
    date = models.DateTimeField(auto_now=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    answer = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '%s para a pergunta "%s" do formulário "%s".'%(self.answer, str(self.question), str(self.form))