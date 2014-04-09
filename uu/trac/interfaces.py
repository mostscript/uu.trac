from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.directives import dexterity, form
from plone.supermodel import model
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from zope.interface import Interface
from zope.interface.common.mapping import IIterableMapping
from zope import schema


# layer interface for product views:

class ITracProductLayer(Interface):
    """Marker for plone.browserlayer"""


# adapter interface:

class ITickets(IIterableMapping):
    """Iterable mapping of tickets, ordered by ticket number"""
    
    def select(query):
        """Given a text query for data source, limit result to some keys"""


# common marker for syncable proxies:

class ITracSyncable(Interface):
    
    def sync():
        """
        Sync local with upstream.  If local content is a listing, then
        sync tickets contained with source, ensure that there is a
        ticket proxy contained for each.  If local content is a ticket
        proxy, then pull down and overwrite ticket metadata.
        """


# content interfaces:

class ITitledTerm(Interface):
    """
    Vocabulary-term interface, with an identifier value, and a
    title value.
    """

    value = schema.TextLine(
        title=u'Identifier',
        required=True,
        )

    title = schema.TextLine(
        title=u'Title',
        required=False,
        )

    note = schema.Text(
        title=u'Note',
        required=False,
        )


class ITracListing(model.Schema, ITracSyncable):
    """Content for trac listing"""

    dexterity.read_permission(url='cmf.ModifyPortalContent')
    dexterity.write_permission(url='cmf.ModifyPortalContent')
    url = schema.BytesLine(
        title=u'URL to Trac (RPC)',
        description=u'XML-RPC URL for Trac server.',
        required=True,
        )

    form.widget(prioritization_categories=DataGridFieldFactory)
    prioritization_categories = schema.List(
        title=u'Prioritization categories',
        description=u'List of prioritization categories for tickets.',
        value_type=DictRow(schema=ITitledTerm),
        defaultFactory=list,
        required=False,
        )

    form.widget(visible_tickets=TextLinesFieldWidget)
    visible_tickets = schema.List(
        title=u'Visible, considered tickets',
        description=u'Enter one ticket number per line.',
        value_type=schema.Int(),
        required=False,
        )

    def select(query):
        """Convienience proxy for ITickets.select()"""


class ITracTicket(model.Schema, ITracSyncable):
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
        required=False,
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
        description=u'Type of task',
        required=False,
        )

    component = schema.BytesLine(
        title=u'Task component area',
        required=False,
        )

    form.omitted('priorities')
    priorities = schema.Dict(
        title=u'Priorities map',
        key_type=schema.TextLine(),
        value_type=schema.Int(),
        required=False,
        )

    def url():
        """Computed hyperlink to ticket in Trac"""

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

    def children(uids=False):
        """
        List child ticket ids, or UUIDs for proxies, if uids is True.
        """

