#!/usr/bin/env python

import os
import pyimgur


class Imgur(object):
    album_dir = None
    album_id = None
    im = None
    output = None
    start_at = 0
    username = None

    def __init__(self, client_id, username=None, album_id=None, start_at=0):
        self.im = pyimgur.Imgur(client_id)
        self.start_at = start_at
        self.username = username if username else 'anonymous'
        self.album_id = album_id
        # Note self.username ref
        self.output = os.path.join('output', self.username)

    def dl(self):
        if self.username is not 'anonymous':
            self.dl_username()
        elif self.album_id:
            self.dl_album_id()

    def dl_username(self):
        # Keep the limit high, default's to 100
        albums = self.im.get_user(self.username).get_albums(limit=1000)
        for index, album in enumerate(albums[self.start_at:], self.start_at):
            images = self.process_album(album, index + 1, len(albums))
            for ix, image in enumerate(images):
                self.image_download(image, ix + 1, len(images))

    def dl_album_id(self):
        albums = [self.im.get_album(self.album_id)]
        for index, album in enumerate(albums):
            images = self.process_album(album, index + 1, len(albums))
            for ix, image in enumerate(images[self.start_at:], self.start_at):
                self.image_download(image, ix + 1, len(images))

    def process_album(self, album, count, total):
        album_name = '%02d - %s - %s' % (count, album.id.lower(), album.title)
        print '(%d/%d) Processing %s' % (count, total, album_name)
        self.check_path(album_name)
        return self.im.get_album(album.id).images

    def check_path(self, album_name):
        self.album_dir = os.path.join(self.output, album_name)
        if not os.path.exists(self.album_dir):
            os.makedirs(self.album_dir)

    def image_download(self, image, count, total):
        image.download(self.album_dir, "%04d - %s" % (count, image.id.lower()))
        print '\t(%d/%d) Dowloaded %s' % (count, total, image.id.lower())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Download albums from imgur.')
    parser.add_argument('client_id', metavar='client-id',  help='imgur api client id')
    parser.add_argument('-u', '--username', help='user account to download (public albums)')
    parser.add_argument('-a', '--album-id', help='album id to download')
    parser.add_argument('-s', '--start-at', type=int, default=0, help='album/image to start at (resume)')
    args = parser.parse_args()

    imgur = Imgur(args.client_id, args.username, args.album_id, args.start_at)
    imgur.dl()
