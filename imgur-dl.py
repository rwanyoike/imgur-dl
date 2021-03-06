#!/usr/bin/env python
from __future__ import print_function

import os
import pyimgur


class Imgur(object):
    """An imgur (http://imgur.com) album downloader."""

    start_at = 0

    def __init__(self, client_id, username=None, album_id=None, start_at=0):
        """Initialize the Imgur object.

        :param client_id: imgur api client id
        :param username: user account to download
        :param album_id: album id to download
        :param start_at: album/image to start at
        """
        self.im = pyimgur.Imgur(client_id)
        self.start_at = start_at
        self.username = username if username else 'anonymous'
        self.album_id = album_id
        self.output = os.path.join('output', self.username)  # self.username ref
        self.album_dir = None

    def dl(self):
        """Download albums by user or album id."""
        if self.username is not 'anonymous':
            self.dl_username()
        elif self.album_id:
            self.dl_album_id()

    def dl_username(self):
        """Download user albums."""
        # Keep the limit high, default's to 100
        albums = self.im.get_user(self.username).get_albums(limit=1000)
        for index, album in enumerate(albums[self.start_at:], self.start_at):
            images = self.process_album(album, index + 1, len(albums))
            for ix, image in enumerate(images):
                self.image_download(image, ix + 1, len(images))

    def dl_album_id(self):
        """Download album by id."""
        albums = [self.im.get_album(self.album_id)]
        for index, album in enumerate(albums):
            images = self.process_album(album, index + 1, len(albums))
            for ix, image in enumerate(images[self.start_at:], self.start_at):
                self.image_download(image, ix + 1, len(images))

    def process_album(self, album, count, total):
        """Return a list of images in an album.

        :param album: Album object
        :param count: image count
        :param total: total images
        :return: a list of the images
        """
        album_name = '{0:02d} - {1} - {2}'.format(count, album.id.lower(), album.title)
        print('({0}/{1}) Processing {2}'.format(count, total, album_name))
        self.make_dirs(album_name)
        return self.im.get_album(album.id).images

    def make_dirs(self, album_name):
        """Create the download directory.

        :param album_name: album name
        """
        self.album_dir = os.path.join(self.output, album_name)
        if not os.path.exists(self.album_dir):
            os.makedirs(self.album_dir)

    def image_download(self, image, count, total):
        """Download an image.

        :param image: Image object
        :param count: image count
        :param total: total images
        """
        image.download(self.album_dir, "{0:04d} - {1}".format(count, image.id.lower()))
        print('\t({0}/{1}) Dowloaded {2}'.format(count, total, image.id.lower()))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Download public albums from imgur.')
    parser.add_argument('client_id', metavar='client-id',  help='imgur api client id')
    parser.add_argument('-u', '--username', help='user account to download (albums)')
    parser.add_argument('-a', '--album-id', help='album id to download')
    parser.add_argument('-s', '--start-at', type=int, default=0, help='album/image to start at (resume)')
    args = parser.parse_args()

    imgur = Imgur(args.client_id, args.username, args.album_id, args.start_at)
    imgur.dl()
