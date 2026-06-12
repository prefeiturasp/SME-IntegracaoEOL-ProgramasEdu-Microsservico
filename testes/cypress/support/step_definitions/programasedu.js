import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

let response

Given('que possuo acesso à API de ProgramasEdu', () => {

  expect(Cypress.env('API_URL')).to.exist
  expect(Cypress.env('API_KEY')).to.exist

})

When('realizo consulta de SRM PAEE do aluno', () => {

  cy.getSrmPaeeAluno()
    .then((res) => {

      response = res

      cy.log(`STATUS => ${res.status}`)
      cy.log(`DURATION => ${res.duration} ms`)

    })

})

Then('o status da resposta de ProgramasEdu deve ser válido', () => {

  expect(response).to.exist

  expect(response.status).to.eq(200)

  expect(response.duration).to.be.lessThan(10000)

  expect(response.body).to.not.be.undefined
  expect(response.body).to.not.be.null

})