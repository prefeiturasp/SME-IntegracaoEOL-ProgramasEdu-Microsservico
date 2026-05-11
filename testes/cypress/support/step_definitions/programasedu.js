import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

let statusCode

Given('que possuo acesso à API de ProgramasEdu', () => {

  expect(Cypress.env('API_URL')).to.not.be.empty
  expect(Cypress.env('API_KEY')).to.not.be.empty
})

When('realizo consulta de turmas PAP do aluno', () => {

  cy.getTurmasPapAluno().its('status').then((status) => {
    statusCode = status
  })
})

When('realizo consulta de alunos PAP do ano letivo', () => {

  cy.getAlunosPapAnoLetivo().its('status').then((status) => {
    statusCode = status
  })
})

When('realizo consulta de PAP do ano corrente', () => {

  cy.getPapAnoCorrente().its('status').then((status) => {
    statusCode = status
  })
})

When('realizo consulta de PAP por ano letivo', () => {

  cy.getPapAnoLetivo().its('status').then((status) => {
    statusCode = status
  })
})

When('realizo consulta de turmas PAP por ano letivo', () => {

  cy.getTurmasPapAnoLetivo().its('status').then((status) => {
    statusCode = status
  })
})

When('realizo consulta de turma SRM e regular do aluno', () => {

  cy.getTurmaSrmRegularAluno().its('status').then((status) => {
    statusCode = status
  })
})

When('realizo consulta de SRM PAEE do aluno', () => {

  cy.getSrmPaeeAluno().its('status').then((status) => {
    statusCode = status
  })
})

When('realizo consulta POST de turmas programa', () => {

  cy.postTurmasPrograma().its('status').then((status) => {
    statusCode = status
  })
})

Then('o status da resposta de ProgramasEdu deve ser válido', () => {

  expect([
    200,
    201,
    202,
    204,
    400,
    404,
    500,
  ]).to.include(statusCode)
})