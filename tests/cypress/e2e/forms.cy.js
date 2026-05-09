const {
  createAdministrativeDivisionCategory,
  createAdministrativeDivisionUnit,
  createDomain,
} = require("../testing/management");

// Expected to be invoked inside a div containing one autocomplete field.
// Waits a bit before pressing enter to give the async operation some time
// to complete.
// If flaky, consider increasing the timeout.
const selectAutocompleteOptionContaining = (selectionElement, text) => {
  selectionElement.click().focused().type(text).wait(1000).type("{enter}");
};

// Fill a TinyMCE editor form.
// Use their JS API instead of talking to the DOM directly.
// Click on the iframe to focus the editor, then set its content via JS.
const fillTinyMceForm = (iframeElement, text) => {
  iframeElement.click();
  cy.window().then((win) => win.eval(`window.tinymce.focusedEditor.setContent(${text})`));
};

const login = (username, password) => {
  cy.visit("/accounts/login/");
  cy.get('input[name="login"]').type(username);
  cy.get('input[name="password"]').type(password);
  cy.get('button[type="submit"]').click();
}


it("should login and use the app forms", () => {
  // The test assumes the user already exists.
  // You can create a user with
  // `docker compose --file docker-compose.yml --file docker-compose.test.yml run web python manage.py createsuperuserwithpassword --username e2e --email e2e@example.com --password e2e --noinput`

  const username = Cypress.env("USERNAME") || "e2e";
  const password = Cypress.env("PASSWORD") || "e2e";

  cy.viewport(1920, 1080);
  cy.task("db:clear");

  createAdministrativeDivisionCategory(cy)({
    id: "1",
    name: "Województwo",
    level: 1,
  });
  createAdministrativeDivisionUnit(cy)({
    name: "Małopolskie",
    level: 1,
    category: "1",
    lft: 1,
    rght: 2,
  });
  createDomain(cy)({
    id: 1,
    name: "example.com",
    active: true,
  });

  login(username, password);
  cy.wait(1000);

  // Create a monitoring.
  cy.visit("/monitoringi/");
  cy.contains("a", "Dodaj monitoring").click();
  cy.wait(1000);

  cy.get('input[name="name"]').type("test");
  cy.get('input[name="subject"]').type("test subject");
  cy.get('textarea[name="description"]').type("test description");
  cy.get('select[name="domain"]').select("example.com");

  fillTinyMceForm(
    cy.get('iframe[id="id_email_footer_ifr"]'),
    '"test footer"'
  );

  cy.wait(1000);
  cy.get('input[type="submit"][value="Zapisz"]').click();

  // Create an institution
  cy.visit("/instytucje/");
  cy.contains("a", "Dodaj instytucj").click();
  cy.wait(1000);

  cy.get('input[name="name"]').type("Testowa Instytucja");
  cy.contains("div", "Jednostka podziału terytorialnego").within(($div) => {
    selectAutocompleteOptionContaining(cy.get(".selection"), "Małopolskie");
  });
  cy.get('input[name="email"]').type("test@example.com");
  cy.get('input[type="submit"][value="Zapisz"]').click();
  cy.wait(1000);

  // Create a case
  cy.visit("/monitoringi/");
  cy.contains("a", "test").click(); // go to the monitoring detail page
  cy.wait(1000);
  cy.contains("a", "Utwórz sprawę").click();
  cy.wait(1000);

  cy.get('input[name="name"]').type("test-case");
  cy.contains("div", "Instytucja").within(($div) => {
    selectAutocompleteOptionContaining(cy.get(".selection"), "Testowa Instytucja");
  });
  cy.get('input[type="submit"][value="Zapisz"]').click();
  cy.wait(1000);

  cy.visit("/sprawy/");

  // Filter cases.
  cy.get('form').first().within(() => {

    cy.contains("div", "Monitoring").within(($div) => {
      selectAutocompleteOptionContaining(
        cy.get(".selection"),
        "test"
      );
    });

    cy.contains("div", "Województwa").within(($div) => {
      selectAutocompleteOptionContaining(
        cy.get(".selection"),
        "Małopolskie"
      );
    });

    cy.wait(1000);

    // Submit the form
    cy.get('button[type="submit"]').click();
  });

  // Verify the case is found
  // Look for a link rather than a name, because the name is also present in the filters form.
  cy.get('body a[href="/sprawy/test-case"]').should('exist');

  // Filter using the datatable view.
  cy.visit("/monitoringi/table/");
  cy.wait(1000);
  cy.contains("td", "test description").should('exist');

  // Fill a column filter with random input. It should no longer find any rows.
  cy.get("table thead input[type='text']").first().type("does-not-exist");
  cy.wait(1000);
  cy.contains("td", "test description").should('not.exist');
  
});
