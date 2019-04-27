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

    def sort_by_attributes(self, playlist, attrs):
        """Recursively sorts the playlist one attribute at a time

        Arguments:
            playlist {list} -- Playlist response object
            attrs {list} -- List of attributes to sort by. List must be
                            mutable.

        Returns:
            [list] -- Sorted playlist - who could've guessed?
        """
        if len(attrs):

            attr = attrs.pop()

            if attr == "artists":
                playlist.sort(key=lambda x: x["artists"][0]["name"].lower())
                return self.sort_by_attributes(playlist, attrs)

            elif attr == "tracks":
                playlist.sort(key=lambda x: x["name"].lower())
                return self.sort_by_attributes(playlist, attrs)

            elif attr == "album_release_date":
                playlist.sort(key=lambda x: x["album"]["release_date"])
                return self.sort_by_attributes(playlist, attrs)

            else:
                raise AttributeError("Invalid attribute provided")

        return playlist

    def sort_playlist(self, playlist_name, sort_by, ready, custom=None,
                      show=False):
        """Sorts playlist lol

        Arguments:
            playlist_name {str} -- Name of the playlist duh. Will raise an
                                   exception if the playlist isn't associated
                                   with the username. Which is also a good
                                   indication the user does not own the
                                   playlist.
            sort_by {list} -- List of attributes to sort by. List must be
                              mutable.
            ready {bool} -- Option to commit changes to the updated playlist.
            custom {func} -- Optional custom sorting key, like if you wanna
                             sort by track name sring length or something.
            show {bool} (default: False) -- Option to dump the reordered
                                              playlist in a purdy format.
        """
        playlists = self.sp.user_playlists(self.user_id)
        new_playlist = []

        for playlist in playlists["items"]:
            if playlist["name"] == playlist_name:
                results = self.sp.user_playlist(
                    self.user_id, playlist["id"], fields="tracks,next"
                )
                tracks = results["tracks"]
                new_playlist.extend([i["track"] for i in tracks["items"]])

                while tracks["next"]:
                    tracks = self.sp.next(tracks)
                    new_playlist.extend([i["track"] for i in tracks["items"]])

                new_playlist = self.sort_by_attributes(new_playlist, sort_by)

                if custom:
                    new_playlist.sort(key=custom)

                if show:
                    print("Playlist name: {}".format(playlist_name))
                    print("Playlist ID: {}\n".format(playlist["id"]))
                    print("   {:3s} {:60s} {:s}".format("", "Track", "Artist"))
                    for i, item in enumerate(new_playlist):
                        track = item
                        print(
                            "   {:3d} {:60s} {:s}".format(
                                i + 1,
                                track["name"],
                                track["artists"][0]["name"]
                            )
                        )

                if ready:
                    self.sp.user_playlist_replace_tracks(
                        self.user_id,
                        playlist["id"],
                        [x["uri"] for x in new_playlist]
                    )
                    print("Playlist successfully updated")
                break

        if not len(new_playlist):
            raise AttributeError("Playlist not found")


if __name__ == "__main__":

    obj = Sortify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, "12164367064")

    # sort by album release date, artist name, track name and of course the
    # third character of each track name lol
    obj.sort_playlist(
        "MMXIX",
        sort_by=["album_release_date", "artists", "tracks"],
        custom=lambda x: x["name"][2],
        ready=False,
        show=True
    )
