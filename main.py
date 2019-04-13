#from tabula import read_pdf, convert_into
import numpy as np
import pandas as pd
from django.db import transaction

from data.models import Course as Curso, Subject as Disciplina

DIAS = (
    ('SEG', 'Segunda-feira'),
    ('TER', 'Terça-feira'),
    ('QUA', 'Quarta-feira'),
    ('QUI', 'Quinta-feira'),
    ('SEX', 'Sexta-feira'),
)

HORARIOS = (
    (7, '07:30 às 9:10'),
    (9, '09:20 às 11:00'),
    (11, '11:10 às 12:50'),
    (13, '13:30 às 15:10'),
    (15, '15:20 às 17:00'),
    (17, '17:10 às 18:50'),
    (19, 'Noite'),
)

def get_subject_data(filename, codigo_curso):
    a = read_pdf(filename, pages='all')
    texto = a['Matricula Nome'][0]
    matricula = texto.split()[0]
    nome = ' '.join(texto.split()[1:])
    print('\n')
    a = a[a['Matricula Nome'].map(lambda x:  isinstance(x, str) and x.startswith(codigo_curso))]
    a = a[a['Ingresso UFAL Ingresso Curso'].map(lambda x: not x is np.nan)]
    a['code'] = a.apply(lambda x: x['Matricula Nome'].split()[0], axis=1)
    a['name'] = a.apply(lambda x: ' '.join(x['Matricula Nome'].split()[1:]), axis=1)
    a['status'] = a.apply(lambda x: x['Ingresso UFAL Ingresso Curso'].split()[-1], axis=1)
    a = a[a['status'].map(lambda x: x != 'MA')]
    a['note'] = a.apply(lambda x: float(x['Ingresso UFAL Ingresso Curso'].split()[0].replace(',','.')), axis=1)
    return nome, matricula, a

def obtem_oferta(filename):
    coluna_codigo = 'CÓDIGO'
    df = pd.read_excel(filename, header=1)
    print(df.head())
    df = df.dropna(subset=[coluna_codigo,])
    df = df[~df[coluna_codigo].isin((coluna_codigo,))]
    return df

def codigo_disciplina(row):
    if row['TURMA'].split(')')[0][-1].isdigit():
        if row['ATIV_REMANESCENTE']!='-':
            return row['ATIV_REMANESCENTE'][:7]
        else:
            return row['TURMA'].split(')')[0][-7:]
    else:
        return False


def obtem_historicos(filename):
    df = pd.read_excel(filename, header=0)
    df['matricula'] = df.apply(lambda x: x['ALUNO'].split(')')[0].strip('( '), axis=1)
    df['nome'] = df.apply(lambda x: x['ALUNO'].split(')')[1], axis=1)
    df['disciplina'] = df.apply(codigo_disciplina, axis=1)
    df = df[df.apply(lambda x: x['disciplina']!=False, axis=1)]
    df = df[df.CONCEITO!='Apto']
    df = df[df.CONCEITO!='Matriculado']
    df = df[df.CONCEITO!='Trancado']
    df = df[df.CONCEITO!='Sem Conceito']
    return df.dropna(subset=['MEDIA_FINAL',])

def obtem_disciplinas(filename):
    df = pd.read_excel(filename, header=0)
    df = df.copy().set_index(df['Código'])
    obrigatorias = df[df['Eletiva'] == 0]
    eletivas = df[df['Eletiva'] == 1]
    obrigatorias['Período'] = pd.Series(obrigatorias['Período']).fillna(method='ffill')
    eletivas = eletivas.dropna(subset=['Período',])
    return obrigatorias, eletivas

def cria_disciplinas(df, eletiva, curso):
    disciplinas = []
    for codigo, nome, periodo, ch in zip(df.index, df['Nome'], df['Período'], df['Carga Horária']):
        print(codigo)
        codigo = codigo[:4] + "%03i"%int(codigo[4:])
        disciplinas.append(Disciplina(
            name=nome.upper(),
            code=codigo,
            grade=int(periodo),
            eletiva=eletiva,
            course=curso,
            #carga_horaria=int(ch.strip('h')),
        ))
    Disciplina.objects.bulk_create(disciplinas)
def cria_turmas(df, curso):
    for codigo, turma, vagas in zip(df['CÓDIGO'], df['TURMA'], df['VAGAS']):
        codigo = codigo[:4] + "%03i"%int(codigo[4:])
        print(codigo)
        disciplina = Disciplina.objects.get(curso=curso, codigo=codigo)
        print(disciplina, turma)
        Turma.objects.create(
            disciplina=disciplina,
            turma=turma.strip(),
            vagas=vagas
        )
def cria_horarios(df):
    horarios_dict = {horario: HORARIO for horario, HORARIO in HORARIOS}
    for dia, DIA in DIAS:
        horarios = df[dia]
        horarios.index = df[['CÓDIGO', 'TURMA']].apply(lambda x: ' '.join(x), axis=1)
        horarios = horarios.dropna()
        for codigo in horarios.index:
            if not codigo.startswith('CÓDIGO'):
                print(df[dia][codigo], codigo)
                horario = DIA + " " + horarios_dict[int(df[dia][codigo].split(':')[0])]
                horario, created = Oferta.objects.get_or_create(horario=horario)
                c = codigo.split()[0]
                turma = codigo.split()[-1]
                c = c[:4] + "%03i"%int(c[4:])
                print(c, turma)
                turma = Turma.objects.get(disciplina__codigo=c, turma=turma.strip())
                horario.disciplinas.add(turma)

def cria_requisitos(df, curso):
    for codigo, requisitos in zip(df.index, df['Pré requisitos']):
        if not requisitos is np.nan:
            d = Disciplina.objects.get(codigo=codigo)
            req = Requisitos.objects.filter(disciplina=d)
            if not req:
                req = Requisitos.objects.create(disciplina=d)
                for r in requisitos.split(','):
                    if '(co)' in r:
                        r = ' '.join([e for e in r.split() if e != '(co)'])
                        print('CO', r)
                        c = Disciplina.objects.get(nome=r.upper(), curso=curso)
                        req.corequisitos.add(c)
                    else:
                        r = ' '.join([e for e in r.split() if e != '(co)'])
                        print('PRE', r)
                        c = Disciplina.objects.get(nome=r.upper(), curso=curso)
                        req.prerequisitos.add(c)

def cria_oferta(filename_oferta, filename_disciplinas, curso):
    #df_obrigatorias, df_eletivas = get_oferta(filename)
    df_obrigatorias, df_eletivas = obtem_disciplinas(filename_disciplinas)
    curso, created = Curso.objects.get_or_create(name=curso)
    cria_disciplinas(df_obrigatorias, False, curso)
    #print('Criou disciplinas obrigatórias')
    #print(df_eletivas)
    cria_disciplinas(df_eletivas, True, curso)
    #print('Criou disciplinas eletivas')
    '''
    #df = obtem_oferta(filename_oferta)
    #print(df)
    #cria_requisitos(df_obrigatorias, curso)
    #cria_requisitos(df_eletivas, curso)
    cria_turmas(df, curso)
    o = Oferta.objects.all()
    if not o:
        horarios = []
        for k, dia in DIAS:
            for k2, hora in HORARIOS:
                horarios.append(Oferta(horario=dia+' '+hora))
        o = Oferta.objects.bulk_create(horarios)
    print('Horários resolvido')
    cria_horarios(df)
    print('Criou horário das obrigatórias')
    print('Criou horário das eletivas')
    '''



def salva_aluno(filename):
    df = obtem_historicos(filename)
    registros = []
    with transaction.atomic():
        for i, subject in df.iterrows():
            if subject.MEDIA_FINAL:
                nota = subject.MEDIA_FINAL
            else:
                nota = 0
            disciplina = Disciplina.objects.filter(codigo=subject.disciplina)
            if disciplina:
                a = RegistroDisciplinaPaga(
                    matricula=subject.matricula,
                    disciplina=disciplina[0],
                    situacao=subject.CONCEITO,
                    nome=subject.nome,
                    nota=nota
                )
                a.save()

    print('Criados históricos')

#MAIN


#

[
    ('Oferta Engenharia Ambiental.xlsx', 'Disciplinas Engenharia Ambiental.xlsx', 'Engenharia Ambiental e Sanitária'),
    ('Oferta Eng Química.xlsx', 'Disciplinas Engenharia Química.xlsx', 'Engenharia Química'),
    ('Oferta Eng Petróleo.xlsx', 'Disciplinas Engenharia Petróleo.xlsx', 'Engenharia do Petróleo'),
    ('Oferta Eng Civil.xlsx', 'Disciplinas Engenharia Civil.xlsx', 'Engenharia Civil'),
]


cria_oferta('Oferta Eng Civil.xlsx', 'Disciplinas Engenharia Civil.xlsx', 'Engenharia Civil'),
#salva_aluno('Históricos Engenharia Ambiental e Sanitária.xlsx')
#salva_aluno('historico-analitico-17212209.pdf', 'ECIV')
