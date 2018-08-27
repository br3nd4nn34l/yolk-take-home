# yolk-take-home

To run the server: `docker-compose up --build`, navigate to localhost:5000
To run tests: `docker-compose -f docker-compose.yml -f docker-compose.test.yml run test`

To get JSON for one ticket: `/tickets/<ticket_id>`
To get JSON for many tickets: `/tickets`
    Parameters (result is the logical AND of these conditions):
        status (appendable): look for all tickets whose status is in this list
        create_lb, create_ub: inclusive lower and upper CREATION date bounds for tickets
        close_lb, close_ub: inclusive lower and upper CLOSING date bounds for tickets

HTML Interfaces:
    To create a ticket: `/create`
    To edit a ticket: `/edit/<ticket_id>`
    To search tickets: `/search`

File Structure:
    app.py - contains code needed to set up the Flask app
    constants.py - defines constants
    data_models.py - defines the MongoEngine ORM classes
    data_resources.py - defines the Flask-Restful resources
    server.py - runs the server
    test.py - runs some tests