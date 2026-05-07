const { defineConfig } = require('cypress');
const db = require('./cypress/plugins/db');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://web:8000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.js',
    video: true,
    videosFolder: 'cypress/videos',
    screenshotsFolder: 'cypress/screenshots',
    setupNodeEvents(on, config) {
      on('task', {
        'db:query': db.query,
        'db:clear': db.clear,
        log(message) {
          console.log(message)
          return null
        },
      });
      return config;
    },
  },
});
