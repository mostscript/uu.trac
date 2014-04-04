import itertools
import xmlrpclib

from zope.interface import implements

from interfaces import ITickets


class TracTickets(object):
    """
    Adapter of trac listing, fronts a read-only mapping of tickets from
    Trac site fetched over XML-RPC.  Key is ticket number integer.
    """
    
    implements(ITickets)

    def __init__(self, context, url=None):
        self.context = context  # site
        if url is None:
            url = self.context.url
        self.proxy = xmlrpclib.ServerProxy(url)

    def __getitem__(self, key):
        v = self.get(key, None)
        if v is None:
            raise KeyError(key)
        return v

    def get(self, key, default=None):
        return self.proxy.ticket.get(int(key))[3]

    def keys(self, q=None):
        if q is None:
            return self.proxy.ticket.query()
        return self.proxy.ticket.query(q)

    def iterkeys(self):
        return iter(self.keys())

    def itervalues(self):
        return itertools.imap(self.get, self.iterkeys())

    def iteritems(self):
        return itertools.imap(
            lambda k: (k, self.get(k)),
            self.iterkeys(),
            )

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())
        
    def __len__(self):
        return len(self.keys())
    
    def __contains__(self, key):
        return key in self.keys()

    def select(self, query):
        return self.keys(query)

    __iter__ = iterkeys

