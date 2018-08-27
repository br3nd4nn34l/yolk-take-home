# Defining all models here

from mongoengine import \
    Document, \
    StringField, DateTimeField, EmailField, \
    EmbeddedDocument, EmbeddedDocumentListField
from enum import Enum

class TicketStatus(Enum):
    Backlog = "backlog"
    Progress = "progress"
    Review = "review"
    Closed = "closed"

class Comment(EmbeddedDocument):
    """
    Represents comments on tickets
    """
    commenter = EmailField(required=True)
    text = StringField(required=True)

class Ticket(Document):
    """
    Represents a ticket
    """
    title = StringField(required=True)
    status = StringField(required=True)
    text = StringField(required=True)
    create_time = DateTimeField(required=True)
    close_time = DateTimeField(required=False)
    delete_time = DateTimeField(required=False)

    creator = EmailField(required=True)
    assignee = EmailField(required=True)

    comments = EmbeddedDocumentListField(Comment)