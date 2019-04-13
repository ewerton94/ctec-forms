# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Course, Subject, Form, Option, Result, Group, Question


admin.site.register(Course)
admin.site.register(Group)
admin.site.register(Subject)
admin.site.register(Form)
admin.site.register(Option)
admin.site.register(Result)
admin.site.register(Question)
