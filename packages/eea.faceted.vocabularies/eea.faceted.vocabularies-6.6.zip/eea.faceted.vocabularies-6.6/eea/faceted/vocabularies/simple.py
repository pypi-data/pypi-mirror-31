""" Simple static vocabularies
"""
from eea.faceted.vocabularies.utils import IVocabularyFactory
from eea.faceted.vocabularies import EEAMessageFactory as _
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


#
# Use catalog
#
class UseCatalogVocabulary(object):
    """ Use catalog vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, *args, **kwargs):
        """ See IVocabularyFactory interface
        """
        items = (
            SimpleTerm('', '', _('No')),
            SimpleTerm('portal_catalog', 'portal_catalog', _('Yes')),
        )
        return SimpleVocabulary(items)


#
# JsTree themes
#
class JsTreeThemes(object):
    """ Widget position in page
    """
    implements(IVocabularyFactory)

    def __call__(self, *args, **kwargs):

        items = (
            SimpleTerm('default', 'default', _('Default')),
            SimpleTerm('classic', 'classic', _('Classic')),
            SimpleTerm('apple', 'apple', _('Apple')),
            SimpleTerm('green', 'green', _('Green')),
        )
        return SimpleVocabulary(items)
