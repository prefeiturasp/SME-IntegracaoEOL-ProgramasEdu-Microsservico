import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

let response

// ======================================================
// GIVEN
// ======================================================

Given('que possuo acesso à API de ProgramasEdu', () => {

  expect(Cypress.env('API_URL')).to.exist
  expect(Cypress.env('API_URL')).to.not.be.empty

  expect(Cypress.env('API_KEY')).to.exist
  expect(Cypress.env('API_KEY')).to.not.be.empty

})

// ======================================================
// WHEN
// ======================================================

When('realizo consulta de SRM PAEE do aluno', () => {

  return cy.getSrmPaeeAluno()
    .then((res) => {

      response = res

      cy.log(`STATUS => ${res.status}`)
      cy.log(`DURATION => ${res.duration} ms`)

    })

})

// ======================================================
// THEN
// ======================================================

Then('retorna o status 200', () => {

  expect(response, 'Response não retornada').to.exist

  expect(response.status).to.eq(200)

})

Then('o status da resposta de ProgramasEdu deve ser válido', () => {

  expect(response, 'Response não retornada').to.exist

  expect(response.status).to.eq(200)

})

Then('o retorno de SRM PAEE do aluno deve ser válido', () => {

  expect(response, 'Response não retornada').to.exist

  expect(response.status).to.eq(200)

  expect(response.body).to.not.be.undefined
  expect(response.body).to.not.be.null

})
