#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from spotipy import Spotify
import spotipy.util as util

from secret import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


class Sortify(object):

    def __init__(self, client_id, client_secret, redirect_uri, user_id):
        """read readme pls

        Arguments:
            client_id {str} -- Client ID for Spotify app
            client_secret {str} -- Client secret for Spotify app
            redirect_uri {str} -- Redirect URI for Spotify app
            user_id {str} -- Your user ID
        """
        self.user_id = user_id

        os.environ["SPOTIPY_CLIENT_ID"] = CLIENT_ID
        os.environ["SPOTIPY_CLIENT_SECRET"] = CLIENT_SECRET
        os.environ["SPOTIPY_REDIRECT_URI"] = REDIRECT_URI

        self.sp = Spotify(
            auth=util.prompt_for_user_token(
                self.user_id,
                "playlist-modify-public"
            )
        )
        self.sp.trace = False

    def sort_by_attributes(self, playlist, attrs, attr_ix):
        """Recursively sorts the playlist one attribute at a time

        Arguments:
            playlist {list(str)} -- Playlist response object.
            attrs {list(str)} -- List of attributes to sort by.
            attr_ix {int} -- Index of the attributes to recurse with.

        Returns:
            {list(str)} -- Sorted playlist - who could've guessed?
        """
        if attr_ix:

            attr = attrs[attr_ix - 1]
            attr_ix -= 1

            if "artists" in attr:
                playlist.sort(key=lambda x: x["artists"][0]["name"].lower())
                if "reversed" in attr:
                    playlist.reverse()
                return self.sort_by_attributes(playlist, attrs, attr_ix)

            elif "tracks" in attr:
                playlist.sort(key=lambda x: x["name"].lower())
                if "reversed" in attr:
                    playlist.reverse()
                return self.sort_by_attributes(playlist, attrs, attr_ix)

            elif "album_release_date" in attr:
                playlist.sort(key=lambda x: x["album"]["release_date"])
                if "reversed" in attr:
                    playlist.reverse()
                return self.sort_by_attributes(playlist, attrs, attr_ix)

            elif "track_number" in attr:
                playlist.sort(key=lambda x: x["track_number"])
                if "reversed" in attr:
                    playlist.reverse()
                return self.sort_by_attributes(playlist, attrs, attr_ix)

            raise AttributeError("Invalid attribute provided. For a customized "
                                 "attribute, use the `custom` parameter.")

        return playlist

    def dump(self, playlist_name, playlist_id, playlist):
        """Dumps the track number, track name and artist in the updated playlist

        Arguments:
            playlist_name {str} -- Parameter name describes itself >:(
            playlist_id {str} -- Parameter name describes itself >:(
            playlist {list(obj)} -- Parameter name describes itself >:(
        """
        print("Playlist name: {}".format(playlist_name))
        print("Playlist ID: {}\n".format(playlist_id))
        print("{:6s} {:60s} {:s}".format("", "Track", "Artist"))
        print("{:6s} {:60s} {:s}".format("", "-----", "------"))
        for i, track in enumerate(playlist):
            print(
                "   {:3d} {:60s} {:s}".format(
                    i + 1,
                    track["name"],
                    track["artists"][0]["name"]
                )
            )

    def sort_playlist(self, playlist_names, sort_by, ready, reverse=False,
                      custom=None, dump=False):
        """Sorts playlist lol

        Arguments:
            playlist_names {list(str)} -- Names of the playlists duh. Will
                                          raise an exception if any playlist
                                          isn't associated with the username.
                                          Which is also a good indication the
                                          user does not own the playlist.
            sort_by {list(str)} -- List of attributes to sort by.
            ready {bool} -- Option to commit changes to the updated playlist.
            custom {func} -- Optional custom sorting key, like if you wanna
                             sort by track name string length or something
                             similarly absurd.
            dump {bool} (default: False) -- Option to dump the reordered
                                            playlist in a purdy format.
        """
        playlists = self.sp.user_playlists(self.user_id)
        new_playlist = []

        for playlist in playlists["items"]:
            if playlist["name"] in playlist_names:

                playlist_names.remove(playlist["name"])
                tracks = self.sp.user_playlist(
                    self.user_id, playlist["id"]
                )["tracks"]
                new_playlist.extend(i["track"] for i in tracks["items"])

                while tracks["next"]:
                    tracks = self.sp.next(tracks)
                    new_playlist.extend(i["track"] for i in tracks["items"])

                new_playlist = self.sort_by_attributes(new_playlist, sort_by,
                                                       len(sort_by))

                if custom:
                    new_playlist.sort(key=custom)

                if reverse:
                    new_playlist.reverse()

                if dump:
                    self.dump(playlist["name"], playlist["id"], new_playlist)

                if ready:
                    self.sp.user_playlist_replace_tracks(
                        self.user_id, playlist["id"],
                        [x["uri"] for x in new_playlist]
                    )
                    print("Playlist successfully updated")

                new_playlist = []

        if len(playlist_names):
            raise AttributeError(
                "Some playlists were not found: {}".format(
                    " ,".join(playlist_names))
            )


if __name__ == "__main__":

    obj = Sortify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, "12164367064")

    obj.sort_playlist(
        ["2019", "2019+"],
        sort_by=["album_release_date", "artists", "tracks"],
        ready=True,
        reverse=True,
        dump=True
    )
