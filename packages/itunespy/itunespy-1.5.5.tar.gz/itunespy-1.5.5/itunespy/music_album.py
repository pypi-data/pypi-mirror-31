#!/usr/bin/python
# Made with <3 by Fran González (@spaceisstrange)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a
#  copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import itunespy
from itunespy import result_item

class MusicAlbum(result_item.ResultItem):
    """
    Defines an Music Album
    """
    def __init__(self, json):
        """
        Initializes the ResultItem class from the JSON provided
        :param json: String. Raw JSON data to fetch information from
        """
        result_item.ResultItem.__init__(self, json)
        self._track_list = []
        self._album_time = None

    def get_tracks(self):
        """
        Retrieves all the tracks of the album if they haven't been retrieved yet
        :return: List. Tracks of the current album
        """
        if not self._track_list:
            tracks = itunespy.lookup(id=self.collection_id, entity=itunespy.entities['song'])[1:]
            for track in tracks:
                self._track_list.append(track)
        return self._track_list

    def get_album_time(self, round_number=2):
        """
        Retrieves all of the track's length and returns the sum of all
        :param round_number: Int. Number of decimals to round the sum
        :return: Int. Sum of all the track's length
        """
        if not self._track_list:
            self.get_tracks()
        if self._album_time is None:
            album_time = 0.0
            for track in self._track_list:
                album_time += track.get_track_time_minutes()
            self._album_time = round(album_time, round_number)
        return self._album_time
