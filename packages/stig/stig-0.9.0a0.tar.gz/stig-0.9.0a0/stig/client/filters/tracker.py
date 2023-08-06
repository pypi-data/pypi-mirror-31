# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
# http://www.gnu.org/licenses/gpl-3.0.txt

"""Filtering TrackerList items by various values"""

from ..ttypes import TorrentTracker
VALUETYPES = TorrentTracker.TYPES
from . import (BoolFilterSpec, Filter, FilterChain, make_cmp_filter)


def _make_cmp_filter(*args, **kwargs):
    return make_cmp_filter(TorrentTracker.TYPES, *args, **kwargs)

class SingleTrackerFilter(Filter):
    DEFAULT_FILTER = 'domain'

    # Filters without arguments
    BOOLEAN_FILTERS = {
        'all': BoolFilterSpec(
            lambda trk: True,
            aliases=('*',),
            description='All trackers'),
        'alive': BoolFilterSpec(
            lambda trk: trk['error'] == '' or trk['status'] == 'inactive',
            description='Trackers we are trying to connect to'),
    }

    COMPARATIVE_FILTERS = {
        'tier'           : _make_cmp_filter('tier',
                                            description='Match VALUE against torrent tier'),
        'domain'         : _make_cmp_filter('domain',
                                            aliases=('dom',),
                                            description='Match VALUE against domain from announce URL'),
        'url-announce'   : _make_cmp_filter('url-announce',
                                            aliases=('an',),
                                            description='Match VALUE against announce URL'),
        'url-scrape'     : _make_cmp_filter('url-scrape',
                                            aliases=('sc',),
                                            description='Match VALUE against scrape URL'),
        'status'         : _make_cmp_filter('status',
                                            aliases=('st',),
                                            description=('Match VALUE against tracker status '
                                                         '(stopped, idle, queued, announcing, scraping)')),
        'error'          : _make_cmp_filter('error',
                                            aliases=('err',),
                                            description='Match VALUE against error message from tracker'),
        'downloads'      : _make_cmp_filter('count-downloads',
                                            aliases=('dns',),
                                            description='Match VALUE against number of known downloads'),
        'leeches'        : _make_cmp_filter('count-leeches',
                                            aliases=('lcs',),
                                            description='Match VALUE against number of known downloading peers'),
        'seeds'          : _make_cmp_filter('count-seeds',
                                            aliases=('sds',),
                                            description='Match VALUE against number of known seeding peers'),
        'last-announce'  : _make_cmp_filter('time-last-announce',
                                            aliases=('lan',),
                                            description='Match VALUE against time of last announce'),
        'next-announce'  : _make_cmp_filter('time-next-announce',
                                            aliases=('nan',),
                                            description='Match VALUE against time of next announce'),
        'last-scrape'    : _make_cmp_filter('time-last-scrape',
                                            aliases=('lsc',),
                                            description='Match VALUE against time of last scrape'),
        'next-scrape'    : _make_cmp_filter('time-next-scrape',
                                            aliases=('nsc',),
                                            description='Match VALUE against time of next scrape'),
    }


class TorrentTrackerFilter(FilterChain):
    """One or more filters combined with & and | operators"""
    filterclass = SingleTrackerFilter
