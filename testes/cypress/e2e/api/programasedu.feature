# language: pt

Funcionalidade: API - ProgramasEdu

  Cenário: Consultar turmas PAP do aluno
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de turmas PAP do aluno
    Então o status da resposta de ProgramasEdu deve ser válido

  Cenário: Consultar alunos PAP do ano letivo
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de alunos PAP do ano letivo
    Então o status da resposta de ProgramasEdu deve ser válido

  Cenário: Consultar PAP do ano corrente
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de PAP do ano corrente
    Então o status da resposta de ProgramasEdu deve ser válido

  Cenário: Consultar PAP por ano letivo
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de PAP por ano letivo
    Então o status da resposta de ProgramasEdu deve ser válido

  Cenário: Consultar turmas PAP por ano letivo
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de turmas PAP por ano letivo
    Então o status da resposta de ProgramasEdu deve ser válido

  Cenário: Consultar turma SRM e regular do aluno PAEE
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de turma SRM e regular do aluno
    Então o status da resposta de ProgramasEdu deve ser válido

  Cenário: Consultar SRM PAEE do aluno
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta de SRM PAEE do aluno
    Então o status da resposta de ProgramasEdu deve ser válido

  Cenário: Consultar turmas programa via POST
    Dado que possuo acesso à API de ProgramasEdu
    Quando realizo consulta POST de turmas programa
    Então o status da resposta de ProgramasEdu deve ser válido