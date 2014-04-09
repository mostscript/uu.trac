from Products.statusmessages.interfaces import IStatusMessage

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

    def priorities(self):
        keys = getattr(
            self.context.__parent__,
            'prioritization_categories',
            [],
            ) or []
        source = self.context.priorities or {}
        return dict((k, source.get(k)) for k in keys)

    def update(self, *args, **kwargs):
        pass  # TODO


class ListingView(TemplatedView):
    """Standard view for a listing"""

    def update(self, *args, **kwargs):
        pass  # TODO


class ListingImport(TemplatedView):
    """View importable tickets, support form for selection"""

    def update(self, *args, **kwargs):
        pass  # TODO

