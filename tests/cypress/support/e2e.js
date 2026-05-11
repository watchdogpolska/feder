// feder/tests/cypress/support/e2e.js
// This is a great place to put global configuration and behavior that modifies Cypress.

Cypress.on('uncaught:exception', (_err, _runnable) => {
  // returning false here prevents Cypress from failing the test
  // eslint-disable-next-line no-console
  console.log('Uncaught exception temporarily ignored');
  return false;
});
