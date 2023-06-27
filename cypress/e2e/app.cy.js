describe('loads the app UI correctly', () => {
  beforeEach(() =>{
    cy.visit(Cypress.config('baseUrl'));
  })
  
  //loading app component
  it('loads app', () => {
    cy.get('#app').should('exist');
    cy.log(`App is up and running at ${Cypress.config('baseUrl')}`)
  })

  //loading header component
  it('loads header', () => {
    cy.get('#idaes-header').should('exist');
  })

  //loading page contents
  it('loads page contents', () => {
    cy.get('#idaes-page-contents').should('exist');
  })

  //loading stream table
  it('loads stream table', () => {
    cy.get('#stream-table').should('exist');
  })
})





// describe(`header component spec`, () => {
//     // it(`should have logo`, () =>{
//     //   cy.visit(Cypress.config('baseUrl'));
//     //   cy.get(`#idaes-logo`).should('have.attr', 'src', 'assets/idaes-logo.png');
//     // })

//     it(`should have correct flowsheet name`, () => {
//       cy.visit(Cypress.config('baseUrl'));
//       cy.get(`#idaes-fs-name`).should('have.text', 'sample_visualization');
//     })
// });

