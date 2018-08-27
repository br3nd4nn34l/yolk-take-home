# Provides functionality for dealing with the database
from datetime import datetime
from flask_restful import Resource, reqparse
from data_models import Ticket, TicketStatus, Comment
import json


# region Parser Functions

def parse_status(raw_status):
    """
    Attempts to convert raw_status into a TicketStatus value
    """
    refined = raw_status.strip().lower()
    return TicketStatus(refined).value


def parse_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        pass

    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass

    return None


def parse_title(title):
    string = str(title)
    if not string.strip():
        raise ValueError("Title cannot be blank")
    return string


# endregion

# region Resources

class TicketResource(Resource):

    def __init__(self):
        # For parsing POST REQUESTS
        self.post_parser = reqparse.RequestParser() \
            .add_argument("assignee", type=str) \
            .add_argument("status", type=parse_status) \
            .add_argument("commenter", type=str) \
            .add_argument("comment", type=str) \

    def get(self, ticket_id):
        return get_ticket_by_id(ticket_id), 200

    def post(self, ticket_id):
        args = self.post_parser.parse_args()

        return update_ticket(
            ticket_id=ticket_id,
            assignee=args['assignee'],
            status=args['status'],
            commenter=args['commenter'],
            comment=args['comment'],
        ), 201


class TicketListResource(Resource):

    def __init__(self):
        # For parsing POST arguments
        self.post_parser = reqparse.RequestParser() \
            .add_argument("title", type=parse_title, required=True) \
            .add_argument("text", type=str, required=True) \
            .add_argument("status", type=parse_status, required=True) \
            .add_argument("creator", type=str, required=True) \
            .add_argument("assignee", type=str, required=True)

        # For parsing GET arguments
        self.get_parser = reqparse.RequestParser() \
            .add_argument("status", action="append", type=parse_status) \
            .add_argument("create_lb", type=parse_datetime) \
            .add_argument("create_ub", type=parse_datetime) \
            .add_argument("close_lb", type=parse_datetime) \
            .add_argument("close_ub", type=parse_datetime)

    def post(self):
        """POST to create a new Ticket"""
        new_ticket = create_ticket(**self.post_parser.parse_args())
        return new_ticket, 201

    def get(self):
        """
        GET all tickets, according to the following parameters.

        status: Looks for tickets whose status is IN this list (if multiple are given).
        No specification is equivalent to specifying all statuses.

        create_lb, create_ub: inclusive lower and upper bounds for creation date (YYYY.MM.DD)
        close_lb, close_ub: inclusive lower and upper bounds for close date (YYYY.MM.DD)

        Only tickets that match the AND of the above conditions will be returned.
        No arguments will return ALL tickets.
        """
        args = self.get_parser.parse_args()

        return get_ticket_list(
            statuses=args["status"],
            lower_create=args["create_lb"], upper_create=args["create_ub"],
            lower_close=args["close_lb"], upper_close=args["close_ub"]
        ), 200


# endregion

# region Resource Functionality

def get_ticket(ticket_id):
    """
    Attempts to retrieve a ticket by id using ticket_id.
    Throws an exception if no such ticket exists.
    """
    ticket = Ticket.objects(id=ticket_id)
    if not ticket:
        raise Exception("{} is not a valid ticket ID".format(ticket_id))
    return ticket[0]


def resource_output(func):
    """
    Takes func which returns a MongoEngine query result,
    and converts it into a dictionary / list of dictionaries.
    """

    def ret(*args, **kwargs):
        return json.loads(func(*args, **kwargs).to_json())

    return ret


@resource_output
def get_ticket_by_id(ticket_id):
    return get_ticket(ticket_id)


@resource_output
def get_ticket_list(statuses,
                    lower_create, upper_create,
                    lower_close, upper_close):
    kwargs = {}

    if statuses:
        kwargs["status__in"] = statuses

    if lower_create:
        kwargs["create_time__gte"] = lower_create

    if upper_create:
        kwargs["create_time__lte"] = upper_create

    if lower_close:
        kwargs["close_time__gte"] = lower_close

    if upper_close:
        kwargs["close_time__lte"] = upper_close

    return Ticket.objects(**kwargs)


@resource_output
def create_ticket(title, text, creator, assignee, status):
    ret = Ticket(
        title=title,
        text=text,
        creator=creator,
        assignee=assignee,
        status=status,
        create_time=datetime.now()
    )

    ret.save()

    return ret


@resource_output
def update_ticket(ticket_id, assignee, status, commenter, comment):
    ticket = get_ticket(ticket_id)

    # Update assignee if it was given
    if assignee is not None and assignee.strip():
        ticket.assignee = assignee.strip()

    # Update status if it was given
    if status is not None:
        if status == TicketStatus.Closed.value:
            ticket.close_time = datetime.now()
        else:
            ticket.close_time = None
        ticket.status = status

    # Add a comment if it was given
    if (commenter is not None and commenter.strip()) and \
            (comment is not None and comment.strip()):
        comment = Comment(commenter=commenter.strip(),
                          text=comment.strip())
        ticket.comments += [comment]

    ticket.save()

    return ticket

# endregion
