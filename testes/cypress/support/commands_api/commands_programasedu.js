Cypress.Commands.add('getTurmasPapAluno', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/v1/programasedu/alunos/${Cypress.env('CODIGO_ALUNO')}/turmas-pap`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    encoding: 'utf8',
    gzip: false,
    log: false,
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('getAlunosPapAnoLetivo', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/v1/programasedu/alunos/alunos-pap/${Cypress.env('ANO_LETIVO')}`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    encoding: 'utf8',
    gzip: false,
    log: false,
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('getPapAnoCorrente', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/v1/programasedu/alunos/pap/ano-corrente`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    encoding: 'utf8',
    gzip: false,
    log: false,
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('getPapAnoLetivo', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/v1/programasedu/alunos/pap/ano-letivo/${Cypress.env('ANO_LETIVO')}`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    encoding: 'utf8',
    gzip: false,
    log: false,
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('getTurmasPapAnoLetivo', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/v1/programasedu/alunos/turmas-pap/${Cypress.env('ANO_LETIVO')}`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    encoding: 'utf8',
    gzip: false,
    log: false,
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('getTurmaSrmRegularAluno', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/v1/programasedu/alunos/paee/turma-srm-e-regular/aluno/${Cypress.env('CODIGO_ALUNO')}`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    encoding: 'utf8',
    gzip: false,
    log: false,
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('getSrmPaeeAluno', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/v1/programasedu/alunos/srm-paee/aluno/${Cypress.env('CODIGO_ALUNO')}`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    encoding: 'utf8',
    gzip: false,
    log: false,
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('postTurmasPrograma', () => {
  return cy.request({
    method: 'POST',
    url: `${Cypress.env('API_URL')}/api/v1/programasedu/turmas/turmas-programa`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    body: {
      anoLetivo: Number(Cypress.env('ANO_LETIVO')),
      codigosTurmas: [Number(Cypress.env('CODIGO_TURMA'))],
    },
    encoding: 'utf8',
    gzip: false,
    log: false,
    failOnStatusCode: false,
  })
})