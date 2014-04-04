from plone.directives import dexterity, form
from plone.supermodel import model
from zope.interface.common.interfaces import IIterableMapping
from zope import schema


# adapter interface:

class ITickets(IIterableMapping):
    """Iterable mapping of tickets, ordered by ticket number"""
    
    def select(query):
        """Given a text query for data source, limit result to some keys"""


# content interfaces:

class ITracListing(model.Schema):
    """Content for trac listing"""

    dexterity.read_permission(url='cmf.ModifyPortalContent')
    dexterity.write_permission(url='cmf.ModifyPortalContent')
    url = schema.BytesLine(
        title=u'URL to Trac (RPC)',
        description=u'XML-RPC URL for Trac server.',
        required=True,
        )

    prioritization_categories = schema.List(
        title=u'Prioritization categories',
        description=u'List of prioritization categories for tickets.',
        value_type=schema.TextLine(),
        defaultFactory=list,
        )

    def sync():
        """
        Sync local tickets contained with source, ensure
        that there is a ticket proxy contained for each.
        """
    
    def select(query):
        """Convienience proxy for ITickets.select()"""


class ITracTicket(model.Schema):
    """
    Content type for ticket proxy.  It is assumed that content will
    have title matching the ticket title (Trac "summary" field). Keywords
    should map to the Subject field.  The identifier (short name) of
    an ITracTicket content item must be the string representation of the
    integer ticket number.
    """

    parent = schema.Int(
        title=u'Parent ticket',
        description=u'Parent ticket number, if applicable.',
        required=False,
        )

    estimate = schema.Float(
        title=u'Estimated hours',
        default=0.0,
        )

    milestone = schema.BytesLine(
        title=u'Iteration',
        description=u'Iteration, milestone, or backlog name.',
        required=False,
        )

    status = schema.BytesLine(
        title=u'Task status',
        default='new',
        )

    task_type = schema.BytesLine(
        title=u'Task type',
        description='Type of task',
        required=False,
        )

    component = schema.BytesLine(
        title=u'Task component area',
        required=False,
        )

    form.omitted('url')
    url = schema.Bytes(
        title=u'Link URL',
        description=u'Computed hyperlink to ticket.',
        readonly=True,
        )

    form.omitted('priorities')
    priorities = schema.Dict(
        title=u'Priorities map',
        key_type=schema.TextLine(),
        value_type=schema.Int(),
        required=False,
        )

    def score():
        """Sum of priority scores"""

    def reward_ratio():
        """
        self.score() / (self.estimate) -- if self.estimate, otherwise,
        return None (as we do not want to rank low hanging fruit
        on a task of unknown effort, and do not trust that a zero
        estimate is accurate.  Returns float.
        """

    def text():
        """
        Get Trac ticket description; should be in TracWiki
        format; displaying this in Plone may best be done in
        overlay using preformatted/plain text view, unless
        there is a facility for rendering.  Assume UTF-8 string.
        """

    def sync():
        """Sync metadata from upstream ticket source."""

    def children(uids=False):
        """
        List child ticket ids, or UUIDs for proxies, if uids is True.
        """

