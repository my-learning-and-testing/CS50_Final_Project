# Board
#### Video Demo:  <https://youtu.be/Ag_5fCMwokY>
#### Description:
Web application for collaborative visualization of document expiration periods.

In everyday life, we use passports, credit cards, driver's licenses, insurance, visas, and more. Each of them has its own expiration date, and it can be challenging to keep track of everything. Discovering an expired credit card, passport, or driver's license during a trip is never pleasant. This application is designed to address this issue.

The application visually represents and compares the duration of document validity from the current moment in time. Users can add information to the database, specifying the document name and its expiration date. It is also possible to indicate a limited validity period (for example, some countries require a passport's expiration date to be at least 6 months) and the time required for renewal. Records can be edited and deleted.

Visualization is presented on a board where users can choose the scale and gradations:

* 1 or 3 months with a daily scale,
* 6 months or 1 year with a weekly scale,
* 5 years with a monthly scale or 10 years, where each cell represents 3 months.

Gradation cells are colored as follows:

* Green - unlimited validity period,
* Yellow - limited validity period,
* Red - time required for renewal.

At the top and bottom, depending on the scale, the month or year corresponding to the end of the cell is displayed.

The board can be sorted alphabetically or by expiration date.

The application is adapted for use on mobile screens. Users can also provide feedback.

Under the hood, there is a lightweight Flask framework that handles interaction with the SQLite database and the user. Stylized CSS HTML pages are generated using Jinja templates. During the development of the application, I used ready-made Bootstrap styles, the Python CS50 library, and a cat from memegen.

    README.md           - you are here
    start.sql           - SQLite commands for creating a database
    data.db             - database with demo data
    app.py              - here is the logic for database queries, sorting, scaling selection, button functionality, and content generation for pages
    helpers.py          - here is the logic for checking input data and handling errors
    templates/
        layout.html     - the foundation of all pages and the logic for displaying the header
        register.html   - registration form for a new account, with data to be saved in the database
        login.html      - login form, with data to be queried in the database
        index.html      - main 'Board' page displaying documents from the database
        editor.html     - form for adding, modifying, and deleting a document from the database
        feedback.html   - feedback form, with data to be saved in the database
        apology.html    - error page
    static/
        styles.css      - ctyles
    flask_session/
        ***********     - cookies for opening a demo account
