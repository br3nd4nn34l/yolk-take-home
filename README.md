# yolk-take-home

To run the server: `docker-compose up --build`, navigate to localhost:5000<br/>
To run tests: `docker-compose -f docker-compose.yml -f docker-compose.test.yml run test`<br/>

GET JSON for one ticket: `/tickets/<ticket_id>`<br/>

POST to update a ticket: `/tickets/<ticket_id>`<br/>
    >Parameters (if commenter and comment are included, adds the comment to the ticket) <br/>
        >> assignee (email) <br/>
        >> status (string - backlog|progress|review|closed)<br/>
        >> commenter (email) <br/>
        >> comment (string) <br/>
        
GET JSON for many tickets: `/tickets`<br/>
    > Parameters (result is the logical AND of these conditions):<br/>
        >> status (appendable): look for all tickets whose status is in this list<br/>
        >> create_lb, create_ub: inclusive lower and upper CREATION date bounds for tickets<br/>
        >> close_lb, close_ub: inclusive lower and upper CLOSING date bounds for tickets<br/>

POST to create a new ticket: `/tickets`<br/>
    > Parameters <br/>
        >> title (string)<br/>
        >> text (string)<br/>
        >> status (string - backlog|progress|review|closed)<br/>
        >> creator (email)<br/>
        >> assignee (email)<br/>

HTML Interfaces:<br/>
    > To create a ticket: `/create`<br/>
    > To edit a ticket: `/edit/<ticket_id>`<br/>
    > To search tickets: `/search`<br/>

File Structure:<br/>
    > app.py - contains code needed to set up the Flask app<br/>
    > constants.py - defines constants<br/>
    > data_models.py - defines the MongoEngine ORM classes, and a Ticket status enum<br/>
    > data_resources.py - defines the Flask-Restful resources<br/>
    > server.py - runs the server<br/>
    > test.py - runs some tests<br/>