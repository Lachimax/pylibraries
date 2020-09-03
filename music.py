import os
import taglib as tl


def check_trailing_slash(path):
    path = str(path)
    if path != "":
        if path[-1] != '\\':
            path += '\\'
    return path


def get_filetype(path):
    pos = -1
    while path[pos] != '.':
        pos = pos - 1
    return path[pos + 1:]


song_filetypes = ['mp3', 'm4a', 'm4p', 'MP3', 'aif', 'm4v', 'Mp3', 'wav', 'mpg']


class SongDictTree:
    def __init__(self, path: str, type: str = 'Google Play Music'):
        """

        :param path: This should be the high-level directory in which the folders named after artists are contained.
        """
        self.path = check_trailing_slash(path)
        self.artists = {}
        self.populate()

    def populate(self):
        print('Building tree...')
        for artist_dir in filter(lambda n: os.path.isdir(self.path + n), os.listdir(self.path)):
            artist_dir = self.path + check_trailing_slash(artist_dir)
            for album_dir in filter(lambda n: os.path.isdir(artist_dir + n), os.listdir(artist_dir)):
                album_dir = artist_dir + check_trailing_slash(album_dir)
                for song in filter(lambda f: get_filetype(f) in song_filetypes, os.listdir(album_dir)):
                    self.add_song(path=album_dir + song)
        print('Done.')

    def add_song(self, path):
        song = Song(path)
        artist = song.tags['ARTIST'][0]
        album = song.tags['ALBUM'][0]
        title = song.tags['TITLE'][0]
        if self.artists.get(artist) is None:
            self.artists[artist] = ArtistDictTree(title=artist)
        if self.artists[artist].get(album) is None:
            self.artists[artist][album] = AlbumDictTree(title=album)
        if self.artists[artist][album].get(title) is None:
            self.artists[artist][album][title] = song
        else:
            print("Attempted to add duplicate song,", title, ';', album, ';', artist)

    def __getitem__(self, item):
        return self.artists[item]

    def __setitem__(self, key, value):
        self.artists[key] = value

    def show_artists(self):
        for artist in self.artists:
            print(artist)

    def show_albums(self):
        for artist in self.artists:
            print(artist)
            self[artist].show_albums(pad=1)

    def show_songs(self):
        for artist in self.artists:
            print(artist)
            self[artist].show_songs(pad=1)

    def count_songs(self):
        num = 0
        for artist in self.artists:
            num += self[artist].count_songs()
        return num

class ArtistDictTree:
    def __init__(self, title: str, path: str = ""):
        """
        :param title:
        :param path: The directory containing the albums by a certain artist.
        """
        self.title = str(title)
        self.path = check_trailing_slash(path)
        self.albums = {}

    def __getitem__(self, item):
        return self.albums[item]

    def __setitem__(self, key, value):
        self.albums[key] = value

    def get(self, item):
        return self.albums.get(item)

    def show_albums(self, pad: int = 0):
        padding = ""
        for i in range(pad):
            padding += "\t"
        for album in self.albums:
            print(padding + album)

    def show_songs(self, pad: int = 0):
        padding = ""
        for i in range(pad):
            padding += "\t"
        for album in self.albums:
            print(padding + album)
            self[album].show_songs(pad=pad + 1)

    def count_songs(self):
        num = 0
        for album in self.albums:
            num += self[album].count_songs()
        return num


class AlbumDictTree:
    def __init__(self, title: str, path: str = ""):
        """

        :param title:
        :param path: The directory containing the songs of an album.
        """
        self.title = str(title)
        self.path = check_trailing_slash(path)
        self.songs = {}

    def __getitem__(self, item):
        return self.songs[item]

    def __setitem__(self, key, value):
        self.songs[key] = value

    def get(self, item):
        return self.songs.get(item)

    def show_songs(self, pad: int = 0):
        padding = ""
        for i in range(pad):
            padding += "\t"
        for song in self.songs:
            print(padding + song)

    def count_songs(self):
        return len(self.songs)


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
    def __init__(self, path: str, title: str = ""):
        self.title = str(title)
        self.path = path
        self.filetype = get_filetype(self.path)
        # print("Loading", self.path)
        self.file = tl.File(self.path)
        # print("Done.")
        self.tags = self.file.tags
