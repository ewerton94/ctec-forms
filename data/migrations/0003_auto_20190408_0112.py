# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-08 01:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20190408_0111'),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('situation', models.BooleanField()),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Course')),
            ],
            options={
                'verbose_name': 'Formulário',
                'ordering': ['id'],
                'verbose_name_plural': 'Formulários',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.CharField(blank=True, max_length=15, null=True)),
                ('name', models.CharField(max_length=1000)),
                ('type', models.CharField(choices=[('radio', 'Múltipla escolha (radio)'), ('select', 'Múltipla escolha (dropdown)'), ('text', 'Aberta (texto)'), ('number', 'Aberta (número)'), ('range', 'Escala de 1 a 10')], max_length=100)),
                ('options', models.ManyToManyField(blank=True, related_name='questions', to='data.Option')),
            ],
            options={
                'verbose_name': 'Pergunta',
                'ordering': ['id'],
                'verbose_name_plural': 'Perguntas',
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('date', models.DateTimeField(auto_now=True)),
                ('answer', models.TextField()),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Form')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Question')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Subject')),
            ],
            options={
                'verbose_name': 'Resultado',
                'verbose_name_plural': 'Resultados',
            },
        ),
        migrations.AddField(
            model_name='form',
            name='questions',
            field=models.ManyToManyField(blank=True, related_name='forms', to='data.Question'),
        ),
    ]
