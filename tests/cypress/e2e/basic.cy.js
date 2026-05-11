describe("landing page", () => {
  it("should render", () => {
    cy.visit("/");
    cy.contains("fedrujmy");
  });
});
