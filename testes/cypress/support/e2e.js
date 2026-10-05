import '@shelex/cypress-allure-plugin'

// Seus comandos
import './commands_api/commands_programasedu'

// Evita quebra de teste
Cypress.on('uncaught:exception', () => false)