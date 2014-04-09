from urllib2 import urlparse

from BTrees.IOBTree import IOBTree
from zope.interface import implements
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList
from plone.dexterity.content import Container, Item
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID

from interfaces import ITracListing, ITracTicket
from adapter import TracTickets


_u = lambda v: v.decode('utf-8') if isinstance(v, str) else v


def listing_change(context, event):
    if context.url:
        context.sync()


class TracListing(Container):
    """Content class for trac listing"""

    implements(ITracListing)

    def __init__(self, id=None, **kwargs):
        super(TracListing, self).__init__(id, **kwargs)
        # manage an index of parent-to-child, int parent ticket id key
        # to PersistentList of int ticket id value:
        self._children = IOBTree()

    def index_parent_child(self, parent, child=None):
        if ITracTicket.providedBy(parent):
            parent = parent.getId()
        if ITracTicket.providedBy(child):
            child = child.getId()
        parent = int(parent)
        child = int(child) if child else None
        self._children[parent] = self._children.get(parent, PersistentList())
        if child is not None:
            self._children[parent].append(child)

    def _adapter(self):
        if getattr(self, '_v_trac_adapter', None) is None:
            self._v_trac_adapter = TracTickets(self)  # adapt once
        return self._v_trac_adapter
    
    def select(self, query):
        return self._adapter().select(query)

    def _add(self, ticket_number, adapter=None):
        adapter = adapter or self._adapter()
        # generated id from title will be str(ticket_number), we
        # then change the title in sync after creation.
        content = createContentInContainer(
            self,
            portal_type='uu.trac.ticket',
            title=unicode(ticket_number),
            )
        content.sync()
        # check for and recursively add child tickets:
        childq = 'parent=~#%s' % ticket_number
        children = adapter.select(childq)
        for child_id in children:
            self._add(child_id, adapter)

    def sync(self):
        adapter = self._adapter()
        self._children = IOBTree()   # reset all parent/child refs
        q = 'status!=closed'
        for number in adapter.select(q):
            if str(number) not in self.objectIds():
                if number in (self.visible_tickets or []):
                    self._add(number, adapter)
            else:
                self.get(str(number)).sync()

    def children_for(self, ticket_number):
        return list(self._children.get(int(ticket_number), []))


class TracTicket(Item):
    
    implements(ITracTicket)

    def __init__(self, id=None, **kwargs):
        super(TracTicket, self).__init__(id, **kwargs)
        self.priorities = PersistentMapping()
        self.estimate = 0.0

    def Title(self):
        return '# %s: %s' % (self.getId(), self.title.encode('utf-8'))

    def _adapter(self):
        if getattr(self, '_v_trac_adapter', None) is None:
            self._v_trac_adapter = self.__parent__._adapter()
        return self._v_trac_adapter

    def sync(self):
        """Sync local metadata with upstream."""
        adapter = self._adapter()
        data = adapter.get(int(self.getId()))
        self._ticket_text = data.get('description', '')
        self.title = _u(data.get('summary', self.getId()))
        self.component = data.get('component', '')
        self.task_type = data.get('type', '')
        self.status = data.get('status', '')
        self.milestone = data.get('milestone', '')
        # estimated hours assumes TimingAndEstimationPlugin
        self.estimate = float(data.get('estimatedhours', 0.0))
        # parent assumes ChildTicketsPlugin
        parent = data.get('parent', '')
        self.parent = int(parent[1:].strip()) if parent else None
        if self.parent:
            self.__parent__.index_parent_child(self.parent, self.getId())
        self.reindexObject()

    def url(self):
        """
        Get the base URL from parent listing, but remove any
        authentication credentials -- then use to construct link
        to ticket.
        """
        baseurl = self.__parent__.url.split('/login')[0]
        parts = urlparse.urlparse(baseurl)
        netloc = parts.netloc
        if '@' in netloc:
            netloc = netloc.split('@')[1]
        base = '%s://%s%s' % (parts.scheme, netloc, parts.path)
        return '/'.join((base, 'ticket', self.getId()))

    def text(self):
        if not getattr(self, '_ticket_text', None):
            self.sync()
        return self._ticket_text

    def children(self, uids=False):
        listing = self.__parent__
        keys = listing.children_for(int(self.getId()))
        keys = filter(lambda k: str(k) in listing, keys)
        if uids:
            _get = lambda k: listing.get(str(k))
            return [IUUID(_get(k)) for k in keys]
        return keys

    def score(self):
        return sum(self.priorities.values())

    def reward_ratio(self):
        if self.estimate > 0.0:
            return self.score() / self.estimate
        return None

