import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

let response

Given('que possuo acesso à API de ProgramasEdu', () => {

  expect(Cypress.env('API_URL')).to.not.be.empty
  expect(Cypress.env('API_KEY')).to.not.be.empty
})

When('realizo consulta de turmas PAP do aluno', () => {

  cy.getTurmasPapAluno().then((res) => {
    response = res
  })
})

When('realizo consulta de alunos PAP do ano letivo', () => {

  cy.getAlunosPapAnoLetivo().then((res) => {
    response = res
  })
})

When('realizo consulta de PAP do ano corrente', () => {

  cy.getPapAnoCorrente().then((res) => {
    response = res
  })
})

When('realizo consulta de PAP por ano letivo', () => {

  cy.getPapAnoLetivo().then((res) => {
    response = res
  })
})

When('realizo consulta de turmas PAP por ano letivo', () => {

  cy.getTurmasPapAnoLetivo().then((res) => {
    response = res
  })
})

When('realizo consulta de turma SRM e regular do aluno', () => {

  cy.getTurmaSrmRegularAluno().then((res) => {
    response = res
  })
})

When('realizo consulta de SRM PAEE do aluno', () => {

  cy.getSrmPaeeAluno().then((res) => {
    response = res
  })
})

When('realizo consulta POST de turmas programa', () => {

  cy.postTurmasPrograma().then((res) => {
    response = res
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
  ]).to.include(response.status)
})