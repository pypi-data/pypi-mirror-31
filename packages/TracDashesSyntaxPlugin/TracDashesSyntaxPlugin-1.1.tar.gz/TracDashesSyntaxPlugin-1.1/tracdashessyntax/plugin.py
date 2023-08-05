# -*- coding: utf-8 -*-
""" Copyright (c) 2008 Martin Scharrer <martin@scharrer-online.de>
    $Id: plugin.py 17129 2018-04-16 18:21:50Z rjollos $
    $HeadURL: https://trac-hacks.org/svn/dashessyntaxplugin/0.11/tracdashessyntax/plugin.py $

    This is Free Software under the GPLv3 license.

    The regexes XML_NAME (unchanged) and NUM_HEADLINE (added 'n'-prefix for all
    names) were taken from trac.wiki.parser and the base code of method
    `_parse_heading` was taken from trac.wiki.formatter which are:
        Copyright (C) 2003-2008 Edgewall Software
        All rights reserved.
    See http://trac.edgewall.org/wiki/TracLicense for details.

"""

from trac.core import Component, implements
from trac.wiki.api import IWikiSyntaxProvider


class DashesSyntaxPlugin(Component):
    """ Trac Plug-in to provide Wiki Syntax for em and en dashes.

        `$Id: plugin.py 17129 2018-04-16 18:21:50Z rjollos $`
    """
    implements(IWikiSyntaxProvider)

    RE_DASH = r"(?P<endash>(?<!-)-{2,3}(?!-))"
    HTML_EN_DASH = "&#8211;"
    HTML_EM_DASH = "&#8212;"

    def _dash(self, formatter, match, fullmatch):
        if match == '--':
            return self.HTML_EN_DASH
        elif match == '---':
            return self.HTML_EM_DASH
        else:
            return match

    def get_wiki_syntax(self):
        yield (self.RE_DASH, self._dash)

    def get_link_resolvers(self):
        return []
