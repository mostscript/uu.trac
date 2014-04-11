from Products.statusmessages.interfaces import IStatusMessage
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from uu.trac.interfaces import ITracListing


class BaseView(object):
   
    status = None
 
    def __init__(self, context, request):
        self.context = context
        self.request = request
        if self.status is None:
            self.status = IStatusMessage(self.request)


class TemplatedView(BaseView):
    
    index = None  # provided by Five view magic

    def update(self, *args, **kwargs):
        pass  # no default operations, subclasses override

    def __call__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        return self.index(*args, **kwargs)


class SyncActionView(BaseView):
    """Menu item acts, sets status, redirects back to context"""

    def __call__(self, *args, **kwargs):
        listing = ITracListing.providedBy(self.context)
        self.context.sync()
        msg = 'Updated %s from upstream data.' % (
            'listing' if listing else 'ticket'
            )
        self.status.addStatusMessage(msg, type='info')
        self.request.response.redirect(self.context.absolute_url())


class TicketVisibilityCheck(BaseView):
    """View used only for checking ticket visibility in TALES conditions"""
    
    status = False  # suppress construction of status adapter

    def is_visible(self):
        listing = self.context.__parent__
        if not getattr(listing, 'visible_tickets', None):
            return False
        return int(self.context.getId()) in listing.visible_tickets

    def __call__(self, *args, **kwargs):
        self.request.response.redirect(self.context.absolute_url())


class ToggleTicketActionView(BaseView):
    """Toggles ticket as hidden or shown in listing"""

    def toggle(self):
        listing = self.context.__parent__
        if not getattr(listing, 'visible_tickets', None):
            listing.visible_tickets = []
        tnum = int(self.context.getId())
        if tnum in listing.visible_tickets:
            listing.visible_tickets.remove(tnum)
            return 'Hiding'
        listing.visible_tickets.append(tnum)
        return 'Making visible'

    def __call__(self, *args, **kwargs):
        context = self.context
        action = self.toggle()
        self.status.addStatusMessage(
            '%s ticket %s from listing.' % (action, context.getId()),
            type='info',
            )
        self.request.response.redirect(context.absolute_url())


class TicketView(TemplatedView):
    """Standard view for a ticket"""

    def _load_priorities(self):
        config = getattr(
            self.context.__parent__,
            'prioritization_categories',
            [],
            ) or []
        _labelpair = lambda term: (term.get('value'), term.get('title'))
        label_pairs = map(_labelpair, config)
        self._priority_keys = zip(*label_pairs)[0]
        self._priority_labels = dict(label_pairs)
        self._priority_values = self.context.priorities or {}

    def priority_label(self, key):
        return self._priority_labels.get(key, key)

    def priority_keys(self):
        return self._priority_keys

    def priorities(self):
        keys = self._priority_keys
        source = self._priority_values
        return dict((k, source.get(k)) for k in keys)

    def save_priorities(self, data=None):
        conv = lambda v: int(v) if v not in (None, '') else None
        if data is None:
            req = self.request
            keys = [k for k in req.form.keys() if k.startswith('priority-')]
            _get = lambda k: req.form.get(k)
            _pair = lambda k: (k.replace('priority-', ''), _get(k))
            data = dict(map(_pair, keys))
        for known in self._priority_keys:
            if known in data:
                self.context.priorities[known] = conv(data.get(known))
        if known:
            notify(ObjectModifiedEvent(self.context))

    def update(self, *args, **kwargs):
        self._load_priorities()
        if self.request.get('REQUEST_METHOD') == 'POST':
            if self.request.get('save.priorities', None) is not None:
                self.save_priorities()


class ListingView(TemplatedView):
    """Standard view for a listing"""

    def save_priorities(self, data=None):
        req = self.request
        savemap = {}
        keys = [k for k in req.form.keys() if k.startswith('priority-')]
        _comp = lambda k: tuple(k.replace('priority-', '').split('-') + [k])
        ckeys = map(_comp, keys)
        # compute a map of priorities to save, keyed by ticket number
        for tid, name, key in ckeys:
            tid = int(tid)
            if tid not in savemap:
                savemap[tid] = {}
            savemap[tid][name] = req.get(key)
        for tid, data in savemap.items():
            ticket = self.context.get(str(tid))
            view = TicketView(ticket, req)
            view._load_priorities()
            view.save_priorities(data)

    def update(self, *args, **kwargs):
        if self.request.get('REQUEST_METHOD') == 'POST':
            if self.request.get('save.priorities', None) is not None:
                self.save_priorities()
            _progress = lambda k: k if 'saveprogress-' in k else None
            _nonempty = lambda k: k is not None
            progress = filter(
                _nonempty,
                map(_progress, self.request.form.keys())
                )
            if progress:
                self.save_priorities()


class ListingImport(TemplatedView):
    """View importable tickets, support form for selection"""

    def update(self, *args, **kwargs):
        pass  # TODO

