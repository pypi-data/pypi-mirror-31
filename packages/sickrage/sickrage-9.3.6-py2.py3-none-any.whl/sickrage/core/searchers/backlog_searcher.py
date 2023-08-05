# Author: echel0n <echel0n@sickrage.ca>
# URL: https://sickrage.ca
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import datetime
import threading

import sickrage
from sickrage.core.common import Quality, DOWNLOADED, SNATCHED, SNATCHED_PROPER, WANTED
from sickrage.core.queues.search import BacklogQueueItem
from sickrage.core.ui import ProgressIndicator


class BacklogSearcher(object):
    def __init__(self, *args, **kwargs):
        self.name = "BACKLOG"
        self.lock = threading.Lock()
        self._last_backlog_search = None
        self.cycleTime = 21 / 60 / 24
        self.amActive = False
        self.amPaused = False
        self.amWaiting = False
        self.forced = False
        self._resetPI()

    def run(self, force=False):
        if self.amActive or sickrage.app.developer and not force:
            return

        # set thread name
        threading.currentThread().setName(self.name)

        # set cycle time
        self.cycleTime = sickrage.app.config.backlog_searcher_freq / 60 / 24

        try:
            self.forced = force
            self.searchBacklog()
        finally:
            self.amActive = False

    def nextRun(self):
        if self._last_backlog_search <= 1:
            return datetime.date.today()
        else:
            return datetime.date.fromordinal(self._last_backlog_search + self.cycleTime)

    def _resetPI(self):
        self.percentDone = 0
        self.currentSearchInfo = {'title': 'Initializing'}

    def getProgressIndicator(self):
        if self.amActive:
            return ProgressIndicator(self.percentDone, self.currentSearchInfo)
        else:
            return None

    def am_running(self):
        sickrage.app.log.debug("amWaiting: " + str(self.amWaiting) + ", amActive: " + str(self.amActive))
        return (not self.amWaiting) and self.amActive

    def searchBacklog(self, which_shows=None):
        if self.amActive:
            sickrage.app.log.debug("Backlog is still running, not starting it again")
            return

        self.amActive = True
        self.amPaused = False

        show_list = sickrage.app.showlist
        if which_shows:
            show_list = which_shows

        curDate = datetime.date.today().toordinal()
        fromDate = datetime.date.fromordinal(1)

        # go through non air-by-date shows and see if they need any episodes
        for curShow in show_list:
            if curShow.paused:
                sickrage.app.log.debug("Skipping backlog for {} because the show is paused".format(curShow.name))
                continue

            self._last_backlog_search = self._get_lastBacklogSearch(curShow.indexerid)

            if not which_shows and self.forced:
                sickrage.app.log.info("Running limited backlog on missed episodes " + str(
                    sickrage.app.config.backlog_days) + " day(s) and older only")
                fromDate = datetime.date.today() - datetime.timedelta(days=sickrage.app.config.backlog_days)
            else:
                sickrage.app.log.info('Running full backlog search on missed episodes for selected shows')

            segments = self._get_segments(curShow, fromDate)

            for season, segment in segments.items():
                self.currentSearchInfo = {'title': curShow.name + " Season " + str(season)}
                sickrage.app.search_queue.put(BacklogQueueItem(curShow, segment))

            if not segments:
                sickrage.app.log.debug(
                    "Nothing needs to be downloaded for {}, skipping".format(curShow.name))

            # don't consider this an actual backlog search if we only did recent eps
            # or if we only did certain shows
            if fromDate == datetime.date.fromordinal(1) and not which_shows:
                self._set_lastBacklogSearch(curShow.indexerid, curDate)

        self.amActive = False
        self._resetPI()

    def _get_segments(self, show, fromDate):
        anyQualities, bestQualities = Quality.splitQuality(show.quality)

        sickrage.app.log.debug("Seeing if we need anything from {}".format(show.name))

        # check through the list of statuses to see if we want any
        wanted = {}
        for result in (x for x in sickrage.app.main_db.get_many('tv_episodes', show.indexerid)
                       if x['season'] > 0 and x['airdate'] > fromDate.toordinal()):

            curStatus, curQuality = Quality.splitCompositeStatus(int(result["status"] or -1))

            # if we need a better one then say yes
            if curStatus not in {WANTED, DOWNLOADED, SNATCHED, SNATCHED_PROPER}:
                continue

            if curStatus != WANTED and curQuality != Quality.UNKNOWN:
                if bestQualities:
                    if curQuality in bestQualities or curQuality > max(bestQualities):
                        continue
                elif curQuality in anyQualities or curQuality > max(anyQualities):
                    continue

            # only fetch if not archive on first match
            if curStatus == DOWNLOADED and show.archive_firstmatch:
                continue

            epObj = show.getEpisode(int(result["season"]), int(result["episode"]))

            if epObj.season not in wanted:
                wanted[epObj.season] = [epObj]
            else:
                wanted[epObj.season].append(epObj)

        return wanted

    def _get_lastBacklogSearch(self, showid):
        sickrage.app.log.debug("Retrieving the last check time from the DB")

        try:
            dbData = sickrage.app.main_db.get('tv_shows', showid)
            return int(dbData["last_backlog_search"])
        except:
            return 1

    def _set_lastBacklogSearch(self, showid, when):
        sickrage.app.log.debug("Setting the last backlog in the DB to {}".format(when))

        dbData = sickrage.app.main_db.get('tv_shows', showid)
        dbData['last_backlog_search'] = when
        sickrage.app.main_db.update(dbData)

    def get_backlog_cycle_time(self):
        return max([sickrage.app.config.daily_searcher_freq * 4, 30])
