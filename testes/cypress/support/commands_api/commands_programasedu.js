function getHeaders() {

  return {
    accept: 'application/json',
    [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
  }

}

Cypress.Commands.add('getSrmPaeeAluno', () => {

  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/alunos/srm-paee/aluno/${Cypress.env('CODIGO_ALUNO')}/`,
    headers: getHeaders(),
    failOnStatusCode: false,
  })

})