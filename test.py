import pytest

from datetime import datetime
from mongoengine import connect, QuerySet

from app import create_app
from constants import TEST_DATABASE, DATABASE_HOST
from data_models import Ticket, TicketStatus

@pytest.fixture
def app():

    # Make a fresh database for testing
    db = connect(TEST_DATABASE, host=DATABASE_HOST)
    db.drop_database(TEST_DATABASE)

    # Turn on debug mode for the application, return for testing
    ret = create_app()
    ret.debug = True
    return ret.test_client()

def compare_ticket_lists(lst1, lst2):
    return list(sorted(lst1, key=lambda x: x.id)) == \
           list(sorted(lst2, key=lambda x: x.id))

#region Unit Tests

def test_get_created_ticket(app):
    """Create a ticket, and attempt to retrieve it again using the API"""

    # Make a ticket, save it, get the ID
    tick = Ticket(
        title="Ticket",
        text="Text",
        creator="creator@gmail.com",
        assignee="assignee@gmail.com",
        status=TicketStatus.Progress.value,
        create_time=datetime.now()
    )

    tick.save()

    # Retrieve the ticket from the app
    resp = app.get("/tickets/{}".format(tick.id))
    assert resp.status_code == 200

    same_tick = Ticket.from_json(resp.data)

    assert tick == same_tick

def test_view_all_tickets(app):
    """Create a bunch of tickets, and attempt to retrieve them all using the API"""
    for i in range(10):
        tick = Ticket(
            title="Ticket {}".format(i),
            text="Text {}".format(i),
            creator="creator{}@gmail.com".format(i),
            assignee="assignee{}@gmail.com".format(i),
            status=TicketStatus.Progress.value,
            create_time=datetime.now()
        )

        tick.save()

    # Retrieve the ticket from the app
    resp = app.get("/tickets")
    assert resp.status_code == 200

    gotten_tickets = QuerySet(Ticket, []).from_json(resp.data)

    assert compare_ticket_lists(gotten_tickets, list(Ticket.objects))

# TODO MORE TESTS: ALL FILTER FUNCTIONALITY (MULTIPLE OPTIONS)

#endregion

#region Integration Tests

def test_ticket_updates(app):
    """
    Creates a ticket, and attempts to use the API to
    change the status of the ticket repeatedly.

    The ticket is checked against the ticket filtering API method
    as it should be the sole ticket in the database.
    """

    # Make a ticket and save it
    tick = Ticket(
        title="Ticket",
        text="Text",
        creator="creator@gmail.com",
        assignee="assignee@gmail.com",
        status=TicketStatus.Progress.value,
        create_time=datetime.now()
    )
    tick.save()

    # Change the status of the ticket using the API
    for status in TicketStatus:

        # Update the ticket
        update_resp = app.post("/tickets/{}".format(tick.id), data={"status" : status.value})
        first_perspective = Ticket.from_json(update_resp.data)

        # Make sure that ticket closure aligns with close time
        # (close time is marked iff closure is checked)
        if status == TicketStatus.Closed:
            assert first_perspective.close_time is not None
        else:
            assert first_perspective.close_time is None

        # Filter by the new status, the ticket should be the only ticket here
        filter_resp = app.get("/tickets", data={"status" : status.value})
        filter_result = QuerySet(Ticket, []).from_json(filter_resp.data)
        assert len(filter_result) == 1
        second_perspective = filter_result[0]

        # Make sure the two perspectives are the same
        assert first_perspective == second_perspective

        # Make sure that filtering on OTHER statuses doesn't make anything appear
        for other_stat in TicketStatus:
            if status.value != other_stat.value:
                other_filter_resp = app.get("/tickets", data={"status": other_stat.value})
                other_filter_result = QuerySet(Ticket, []).from_json(other_filter_resp.data)
                assert len(other_filter_result) == 0

#endregion