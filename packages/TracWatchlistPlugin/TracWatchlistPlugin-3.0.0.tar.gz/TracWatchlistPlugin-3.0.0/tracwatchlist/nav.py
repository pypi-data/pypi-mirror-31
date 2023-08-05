# -*- coding: utf-8 -*-
#
# Copyright (c) 2008-2010 by Martin Scharrer <martin@scharrer-online.de>
# All rights reserved.
#
# The i18n support was added by Steffen Hoffmann <hoff.st@web.de>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License see
# <http://www.gnu.org/licenses/>.

from trac.core import Component, implements
from trac.util.html import tag
from trac.web.chrome import INavigationContributor

from tracwatchlist.translation import _


class WatchlistNavigation(Component):
    """Navigation entries for the Trac WatchlistPlugin."""
    implements(INavigationContributor)

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        if req.path_info.startswith("/watchlist"):
            return 'watchlist'
        return ''

    def get_navigation_items(self, req):
        user = req.authname
        if user and user != 'anonymous':
            yield ('mainnav', 'watchlist',
                   tag.a(_("Watchlist"), href=req.href("watchlist")))
