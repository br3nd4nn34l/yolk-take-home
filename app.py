from flask import Flask, render_template
from flask_restful import Api
from data_resources import TicketListResource, TicketResource, get_ticket

def create_app():

    # Start the app and attach API resources to it
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(TicketListResource, '/tickets')
    api.add_resource(TicketResource, '/tickets/<ticket_id>')

    # Attach pages to the app
    @app.route('/')
    @app.route('/search')
    def root():
        return render_template("search.html")

    @app.route('/create')
    def create():
        return render_template("create.html")

    @app.route('/edit/<ticket_id>')
    def view(ticket_id):
        return render_template("edit.html", ticket=get_ticket(ticket_id))

    return app