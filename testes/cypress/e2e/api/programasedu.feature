# language: pt

Funcionalidade: API - ProgramasEdu

  Cenário: Consultar turmas PAP do aluno
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de turmas PAP do aluno
    Então retorna o status 200 
    E o retorno de turmas PAP do aluno deve ser válido

# @ignore
  Cenário: Consultar alunos PAP do ano letivo
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de alunos PAP do ano letivo
    Então retorna o status 200
    E o retorno de alunos PAP do ano letivo deve ser válido

@ignore
  Cenário: Consultar PAP do ano corrente
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de PAP do ano corrente
    Então retorna o status 200
    E o retorno de PAP do ano corrente deve ser válido

  Cenário: Consultar PAP por ano letivo
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de PAP por ano letivo
    Então retorna o status 200
    E o retorno de PAP por ano letivo deve ser válido

  Cenário: Consultar turmas PAP por ano letivo
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de turmas PAP por ano letivo
    Então retorna o status 200
    E o retorno de turmas PAP por ano letivo deve ser válido

  Cenário: Consultar turma SRM e regular do aluno PAEE
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de turma SRM e regular do aluno
    Então retorna o status 200
    E o retorno de turma SRM e regular do aluno deve ser válido

  Cenário: Consultar SRM PAEE do aluno
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de SRM PAEE do aluno
    Então retorna o status 200
    E o retorno de SRM PAEE do aluno deve ser válido

  Cenário: Consultar turmas programa via POST
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta POST de turmas programa
    Então retorna o status 200
    E o retorno de turmas programa deve ser válido