import os
import taglib as tl


def check_trailing_slash(path):
    path = str(path)
    if path[-1] != '\\':
        path += '\\'
    return path


def get_filetype(path):
    pos = -1
    while path[pos] != '.':
        pos = pos - 1
    return path[pos + 1:]


song_filetypes = ['mp3', 'm4a', 'm4p', 'MP3', 'aif', 'm4v', 'Mp3', 'wav', 'mpg']


class SongTree:
    def __init__(self, path: str, type: str = 'iTunes'):
        """

        :param path: This should be the high-level directory in which the folders named after artists are contained.
        """
        self.path = check_trailing_slash(path)
        self.artists = self.get_artists()

    def __getitem__(self, item):
        return self.artists[item]

    def get_artists(self):
        print("Building tree...")
        artist_list = filter(lambda n: os.path.isdir(self.path + n), os.listdir(self.path))
        artists = []
        for artist in artist_list:
            artists.append(Artist(title=artist, path=self.path + artist + '\\'))
        print("Done.")
        return artists

    def show_artists(self):
        for artist in self.artists:
            print(artist.title)

    def show_albums(self):
        for artist in self.artists:
            print(artist.title)
            artist.show_albums(pad=1)

    def show_songs(self):
        for artist in self.artists:
            print(artist.title)
            artist.show_songs(pad=1)

    def count_songs(self):
        num = 0
        for artist in self.artists:
            num += artist.count_songs()
        return num

    def all_filetypes(self):
        filetypes = []
        for artist in self.artists:
            ft = artist.all_filetypes()
            for filetype in ft:
                if filetype not in filetypes:
                    filetypes.append(filetype)

        return filetypes


class Artist:
    def __init__(self, title: str, path: str):
        """

        :param title:
        :param path: The directory containing the albums by a certain artist.
        """
        self.title = str(title)
        self.path = check_trailing_slash(path)
        self.albums = self.get_albums()

    def __getitem__(self, item):
        return self.albums[item]

    def get_albums(self):
        album_list = filter(lambda n: os.path.isdir(self.path + n), os.listdir(self.path))
        albums = []
        for album in album_list:
            albums.append(Album(title=album, path=self.path + album + '\\'))
        return albums

    def show_albums(self, pad: int = 0):
        padding = ""
        for i in range(pad):
            padding += "\t"
        for album in self.albums:
            print(padding + album.title)

    def show_songs(self, pad: int = 0):
        padding = ""
        for i in range(pad):
            padding += "\t"
        for album in self.albums:
            print(padding + album.title)
            album.show_songs(pad=pad + 1)

    def count_songs(self):
        num = 0
        for album in self.albums:
            num += album.count_songs()
        return num

    def all_filetypes(self):
        filetypes = []
        for album in self.albums:
            ft = album.all_filetypes()
            for filetype in ft:
                if filetype not in filetypes:
                    filetypes.append(filetype)

        return filetypes


class Album:
    def __init__(self, title: str, path: str):
        """

        :param title:
        :param path: The directory containing the songs of an album.
        """
        self.title = str(title)
        self.path = check_trailing_slash(path)
        self.songs = self.get_songs()

    def __getitem__(self, item):
        return self.songs[item]

    def get_songs(self):
        song_list = filter(lambda f: get_filetype(f) in song_filetypes, os.listdir(self.path))
        songs = []
        for song in song_list:
            songs.append(Song(title=song, path=self.path + song))
        return songs

    def show_songs(self, pad: int = 0):
        padding = ""
        for i in range(pad):
            padding += "\t"
        for song in self.songs:
            print(padding + song.title)

    def count_songs(self):
        return len(self.songs)

    def all_filetypes(self):
        filetypes = []
        for song in self.songs:
            if song.filetype not in filetypes:
                filetypes.append(song.filetype)
        return filetypes


class Song:
    def __init__(self, title: str, path: str):
        self.title = str(title)
        self.path = path
        self.filetype = get_filetype(self.path)
        #self.file = tl.File(self.path)
