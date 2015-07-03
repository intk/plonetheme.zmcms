from zope.interface import Interface
from zope import schema
from plonetheme.zmcms import MessageFactory as _

class IMediaTypes(Interface):
    """
    Marks all Media types from Products.media*
    """
    