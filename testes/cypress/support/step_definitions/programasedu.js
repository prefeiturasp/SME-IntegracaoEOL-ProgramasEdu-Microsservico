import { Given, When, Then } from "cypress-cucumber-preprocessor/steps";

let statusCode;

Given("que possuo acesso à API de ProgramasEdu", () => {
  expect(Cypress.env("API_URL")).to.not.be.empty;
});

When("realizo consulta de turmas PAP do aluno", () => {
  cy.getTurmasPapAluno().as("response");
});

When("realizo consulta de alunos PAP do ano letivo", () => {
  cy.getAlunosPapAnoLetivo().as("response");
});

When("realizo consulta de PAP do ano corrente", () => {
  cy.getPapAnoCorrente().as("response");
});

When("realizo consulta de PAP do ano corrente", () => {
  cy.getPapAnoCorrente().as("response");
});

When("realizo consulta de PAP por ano letivo", () => {
  cy.getPapAnoLetivo().as("response");
});

When("realizo consulta de turmas PAP por ano letivo", () => {
  cy.getTurmasPapAnoLetivo().as("response");
});

When("realizo consulta de turma SRM e regular do aluno", () => {
  cy.getTurmaSrmRegularAluno().as("response");
});

When("realizo consulta de SRM PAEE do aluno", () => {
  cy.getSrmPaeeAluno().as("response");
});

When("realizo consulta POST de turmas programa", () => {
  cy.postTurmasPrograma().as("response");
});

// THEN

Then("retorna o status 200", function () {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(200);
  });
});

Then("retorna o status 400", function () {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(400);
  });
});

Then("retorna o status 404", function () {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(404);
  });
});

// AND

And("o retorno de turmas PAP do aluno deve ser válido", function () {
  cy.get("@response").then((response) => {
    expect(response.body[0]).to.have.property("codigo_aluno");
    expect(response.body[0]).to.have.property("codigo_turma");
    expect(response.body[0]).to.have.property("codigo_componente_curricular");
    expect(response.body[0]).to.have.property("nome_componente_curricular");
  });
});

And("o retorno de alunos PAP do ano letivo deve ser válido", function () {
  cy.get("@response").then((response) => {
    expect(response.body).to.empty;
  });
});

And("o retorno de PAP do ano corrente deve ser válido", function () {
  cy.get("@response").then((response) => {
    expect(response.body[0]).to.have.property("ano_letivo");
  });
});

And("o retorno de PAP por ano letivo deve ser válido", function () {
  cy.get("@response").then((response) => {
    expect(response.body).to.empty;
  });
});

And("o retorno de turmas PAP por ano letivo deve ser válido", function () {
  cy.get("@response").then((response) => {
    expect(response.body[0]).to.have.property("codigo_turma");
    expect(response.body[0]).to.have.property("turma_nome");
  });
});

And("o retorno de turma SRM e regular do aluno deve ser válido", function () {
  cy.get("@response").then((response) => {
    expect(response.body).to.empty;
  });
});

And("o retorno de SRM PAEE do aluno deve ser válido", function () {
  cy.get("@response").then((response) => {
    expect(response.body).to.empty;
  });
});

And("o retorno de turmas programa deve ser válido", function () {
  cy.get("@response").then((response) => {
    expect(response.body).to.be.not.empty;
  });
});
