#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from spotipy import Spotify
import spotipy.util as util

from secret import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


class Sortify(object):

    def __init__(self, client_id, client_secret, redirect_uri, user_id):

        self.user_id = user_id

        os.environ["SPOTIPY_CLIENT_ID"] = CLIENT_ID
        os.environ["SPOTIPY_CLIENT_SECRET"] = CLIENT_SECRET
        os.environ["SPOTIPY_REDIRECT_URI"] = REDIRECT_URI

        scope = "playlist-modify-public"
        token = util.prompt_for_user_token(self.user_id, scope)

        self.sp = Spotify(auth=token)
        self.sp.trace = False

    def sort_by_attributes(self, playlist, attrs):

        if len(attrs):

            attr = attrs.pop()

            if attr == "artists":
                playlist.sort(key=lambda x: x["track"]
                              ["artists"][0]["name"].lower())
                return self.sort_by_attributes(playlist, attrs)

            elif attr == "tracks":
                playlist.sort(key=lambda x: x["track"]["name"].lower())
                return self.sort_by_attributes(playlist, attrs)

            elif attr == "album_release_date":
                playlist.sort(key=lambda x: x["track"]["album"]["release_date"])
                return self.sort_by_attributes(playlist, attrs)

            else:
                raise AttributeError("Invalid attribute provided")

        return playlist

    def sort_playlist(self, playlist_name, sort_by, show=False):

        playlists = self.sp.user_playlists(self.user_id)
        sorted_playlist = []

        for playlist in playlists["items"]:
            if playlist["name"] == playlist_name:
                results = self.sp.user_playlist(
                    self.user_id, playlist["id"], fields="tracks,next"
                )
                tracks = results["tracks"]
                sorted_playlist.extend(tracks["items"])

                while tracks["next"]:
                    tracks = self.sp.next(tracks)
                    sorted_playlist.extend(tracks["items"])

                sorted_playlist = self.sort_by_attributes(
                    sorted_playlist, sort_by)

                if show:
                    print("Playlist name: {}".format(playlist_name))
                    print("Playlist ID: {}\n".format(playlist["id"]))
                    print("   {:3s} {:60s} {:s}".format("", "Track", "Artist"))
                    for i, item in enumerate(sorted_playlist):
                        track = item["track"]
                        print(
                            "   {:3d} {:60s} {:s}".format(
                                i + 1,
                                track["name"],
                                track["artists"][0]["name"]
                            )
                        )

                self.sp.user_playlist_replace_tracks(
                    self.user_id,
                    playlist["id"],
                    [x["track"]["uri"] for x in sorted_playlist]
                )
                print("Playlist successfully updated")
                break

        if not len(sorted_playlist):
            raise AttributeError("Playlist not found")


if __name__ == "__main__":

    obj = Sortify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, "12164367064")
    obj.sort_playlist(
        "MMXIX",
        sort_by=["album_release_date", "artists", "tracks"],
        show=True
    )
