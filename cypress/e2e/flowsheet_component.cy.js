describe(
    'flowsheet visualizer component spec',
    {
        retries: {
            runMode: 5,
            openMode: 5
        }
    },
    () => {
        // initial wait time for cypress delay give fetch api some time to call backend
        const waitTime = 300;

        // define visit app url before each test
        beforeEach(() => {
            cy.visit(Cypress.config('baseUrl'));
        });

        // all component's header button are changed these test may update or remove (start)
        // check flowsheet header component exists and visible
        it('check flowsheet header component exists and visible', () => {
            // header component exists
            cy.get('#flowsheet-header-component').should('be.visible');
        })

        // check flowsheet header contain title and title is correct
        it('check flowsheet header contain title and title is correct', () => {
            cy.get('#flowsheet-header-component-title').should('has.text', 'FLOWSHEET')
        })

        // check flowsheet header has all required button exist and visible
        it('check flowsheet header component\'s functions button exists', () => {
            // initial header button as an array
            const buttons = [
                {id: '#stream-names-toggle', name: 'Stream Names Toggle'},
                {id: '#show-label-toggle', name: 'Show Label Toggle'},
                {id: '#zoom-in-btn', name: 'Zoom In'},
                {id: '#zoom-out-btn', name: 'Zoom Out'},
                {id: '#zoom-to-fit', name: 'Zoom To Fit'},
                {id: '#minimize-flowsheet-panel-btn', name: 'Minimize Flowsheet Panel'},
            ];

            // loop through buttons array run each test
            buttons.forEach(button => {
                cy.get(`#flowsheet-header-component ${button.id}`).then($el => {
                    expect($el).to.be.visible, `${button.name} button should be visible`;
                });
            });
        });

        // test flowsheet header component buttons
        // stream names button
        it('test flowsheet header component stream names button', () => {
        })

        // label button
        it('test flowsheet header component label button', () => {
        })

        // zoom in button
        // basic zoom in function
        it('test zoom in button', () => {
            cy.wait(waitTime)
            cy.get('.joint-paper.joint-theme-default').then($el => {
                // record old joint paper element width
                const oldWidth = $el.width();
                const oldHeight = $el.height();

                // click zoom in btn
                cy.get('#zoom-in-btn').click();

                // read joint paper element again
                cy.get('.joint-paper.joint-theme-default').then($newEl => {
                    const newWidth = $newEl.width();
                    const newHeight = $newEl.height();

                    expect(newWidth).to.be.greaterThan(oldWidth);
                    expect(newHeight).to.be.greaterThan(oldHeight);
                });
            });
        });

        // zoom out button
        // basic zoom out function
        it('test zoom out button', () => {
            cy.wait(waitTime)
            cy.get('.joint-paper.joint-theme-default').then($el => {
                // record old joint paper element width
                const oldWidth = $el.width();
                const oldHeight = $el.height();

                // click zoom in btn
                cy.get('#zoom-out-btn').click();

                // read joint paper element again
                cy.get('.joint-paper.joint-theme-default').then($newEl => {
                    const newWidth = $newEl.width();
                    const newHeight = $newEl.height();

                    expect(newWidth).to.be.lessThan(oldWidth);
                    expect(newHeight).to.be.lessThan(oldHeight);
                });
            });
        })

        // zoom to fit button
        it('test zoom to fit button', () => {
            cy.wait(waitTime);
            // read joint paper element when load as default
            cy.get('.joint-paper.joint-theme-default').then($el => {
                // record default joint paper width height
                const defaultWidth = $el.width();
                const defaultHeight = $el.height();

                // change flowsheet size zoom in x 3
                cy.get('#zoom-in-btn').click();
                cy.get('#zoom-in-btn').click();
                cy.get('#zoom-in-btn').click();

                // read joint paper element after zoom in
                cy.get('.joint-paper.joint-theme-default').then($newEl => {
                    // record zoom in joint paper width height
                    const newWidth = $newEl.width();
                    const newHeight = $newEl.height();

                    // make sure zoom in joint paper width and height is greater than default
                    expect(newWidth).to.be.greaterThan(defaultWidth);
                    expect(newHeight).to.be.greaterThan(defaultHeight);

                    // trigger zoom to fit
                    cy.get('#zoom-to-fit').click();

                    // read joint paper element after zoom to fit
                    cy.get('.joint-paper.joint-theme-default').then($elAfterClickZoomToFit => {
                        // record joint paper width height after click zoom to fit
                        const elWidthAfterClickZoomToFit = $elAfterClickZoomToFit.width();
                        const elHeightAfterClickZoomToFit = $elAfterClickZoomToFit.height();

                        // final check
                        expect(elWidthAfterClickZoomToFit === defaultWidth)
                        expect(elHeightAfterClickZoomToFit === defaultHeight)
                    })
                })

            })

        })

        // check flowsheet fv container only has 1 child
        it('check flowsheet fv container only has 1 child', () => {
            cy.get('#fvContainer').children().should('have.length', 1);
        })

        // check has flowsheet jointjs svg diagram
        it('has jointjs diagram', () => {
            cy.get('#fv div.joint-paper svg');
        });


        // check header full window button functions:

        // all component's header button are changed these test may update or remove (end)
    })