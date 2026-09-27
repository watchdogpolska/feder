describe("landing page", () => {
  it("should render", () => {
    cy.visit("/");
    cy.contains("fedrujmy");
    cy.wait(1000);
    cy.screenshot("landing", {capture: "viewport"});
  });
});
