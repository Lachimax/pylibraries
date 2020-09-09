import os
import taglib as tl
import csv


def check_trailing_slash(path):
    path = str(path)
    if path != "":
        if path[-1] != '\\':
            path += '\\'
    return path


def get_filetype(path):
    pos = -1
    while abs(pos) <= len(path):
        if path[pos] == '.':
            return path[pos + 1:]
        pos = pos - 1
    return 'directory'


song_filetypes = ['mp3', 'm4a', 'm4p', 'MP3', 'aif', 'm4v', 'Mp3', 'wav', 'mpg']
library_types = ['itunes', 'google play music', 'takeout', 'comparison']


class SongDictTree:
    def __init__(self, path: str = None, library_type: str = 'Google Play Music', delete_duplicate: bool = False):
        """

        :param path: This should be the high-level directory in which the folders named after artists are contained.
        """

        self.artists = {}
        if library_type.lower() in library_types:
            self.type = library_type.lower()
        else:
            raise ValueError("Only library types ", library_types, "accepted.")

        if path is not None:
            self.path = check_trailing_slash(path)
            self.populate(delete_duplicate=delete_duplicate)
        else:
            self.path = None

    def __getitem__(self, item):
        return self.artists[item]

    def __setitem__(self, key, value):
        self.artists[key] = value

    def get(self, item):
        return self.artists.get(item)

    def populate(self, delete_duplicate: bool = False):
        print('Building tree...')
        self.add_directory(path=self.path, recurse=True, delete_duplicate=delete_duplicate)
        print('Done.')

    def add_directory(self, path, recurse: bool = False, delete_duplicate: bool = False):
        path = check_trailing_slash(path)
        print(path)
        for song in filter(lambda f: get_filetype(f) in song_filetypes, os.listdir(path)):
            self.add_song(path=path, filename=song, delete_duplicate=delete_duplicate)
        if recurse:
            for directory in filter(lambda n: os.path.isdir(path + n), os.listdir(path)):
                self.add_directory(path=path + directory, recurse=True, delete_duplicate=delete_duplicate)

    def add_song(self, path: str, filename: str, delete_duplicate: bool = False):
        print(path)
        path = check_trailing_slash(path) + filename
        song = Song(path)

        if song.tags.get('ARTIST') in [None, []]:
            if song.tags.get('ALBUMARTIST') in [None, []]:
                artist = 'None'
            else:
                artist = song.tags['ALBUMARTIST'][0]
        else:
            artist = song.tags['ARTIST'][0]
        song.artist = artist
        if self.artists.get(artist) is None:
            self.artists[artist] = ArtistDictTree(title=artist)
        self.artists[artist].add_song(song, path=path, filename=filename, delete_duplicate=delete_duplicate)

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

    def compare(self, other: 'SongDictTree'):
        """
        Returns a new SongDictTree containing the artists present in this tree but missing in the other, etc.
        :param other:
        :return:
        """
        missing_artists = SongDictTree(library_type='comparison')
        for artist_name in self.artists:
            artist = self[artist_name]
            if other.get(artist.title) is None:
                missing_artists[artist.title] = artist
            else:
                missing_albums = artist.compare(other[artist.title])
                if len(missing_albums) > 0:
                    missing_artists[artist.title] = missing_albums
        return missing_artists

    def csv(self):
        rows = []
        for artist in self.artists:
            artist = self.artists[artist]
            rows.extend(artist.csv())
        return rows

    def write_csv(self, path):
        if path[-4:] != '.csv':
            path += '.csv'
        rows = self.csv()
        rows.sort(key=lambda r: (r[0], r[1]))
        header = ['Artist', 'Album', 'Title']
        # writing to csv file
        with open(path, 'w', newline='', encoding="utf-8") as csv_file:
            # creating a csv writer object
            csv_writer = csv.writer(csv_file)
            # writing the fields
            csv_writer.writerow(header)
            # writing the data rows
            csv_writer.writerows(rows)


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

    def __len__(self):
        return len(self.albums)

    def get(self, item):
        return self.albums.get(item)

    def add_song(self, song: 'Song', path: str, filename: str, delete_duplicate: bool = False):
        if song.tags.get('ALBUM') in [None, []]:
            album = 'None'
        else:
            album = song.tags['ALBUM'][0]
        song.album = album
        if self.get(album) is None:
            self[album] = AlbumDictTree(title=album, artist=self.title)
        self.albums[album].add_song(song, path=path, filename=filename, delete_duplicate=delete_duplicate)

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

    def compare(self, other: 'ArtistDictTree'):
        """
        Returns a new ArtistDictTree containing the albums present in this artist but missing in the other; it will also
        include albums present in both but missing songs in the other, with those songs listed.
        :param other:
        :return:
        """
        missing_albums = ArtistDictTree(self.title)
        for album_name in self.albums:
            album = self[album_name]
            if other.get(album.title) is None:
                missing_albums[album.title] = album
            else:
                missing_songs = album.compare(other[album.title])
                if len(missing_songs) > 0:
                    missing_albums[album.title] = missing_songs
        return missing_albums

    def csv(self):
        rows = []
        for album in self.albums:
            album = self.albums[album]
            rows.extend(album.csv())
        return rows


class AlbumDictTree:
    def __init__(self, title: str, artist: str = "", path: str = ""):
        """

        :param title:
        :param path: The directory containing the songs of an album.
        """
        self.title = str(title)
        self.path = check_trailing_slash(path)
        self.artist = artist
        self.songs = {}

    def __getitem__(self, item):
        return self.songs[item]

    def __setitem__(self, key, value):
        self.songs[key] = value

    def __len__(self):
        return len(self.songs)

    def get(self, item):
        return self.songs.get(item)

    def add_song(self, song: 'Song', path: str = '', filename: str = '', set_title: bool = True,
                 delete_duplicate: bool = False):

        if set_title:
            if song.tags.get('TITLE') in [None, []]:
                title = filename
            else:
                title = song.tags['TITLE'][0]
            song.title = title
        if self.get(song.title) is None:
            self[song.title] = song
        else:
            print("Attempted to add duplicate song,", song.title, ';', song.album, ';', song.artist)
            if delete_duplicate:
                print('Deleting duplicate file.')
                os.remove(path)

    def show_songs(self, pad: int = 0):
        padding = ""
        for i in range(pad):
            padding += "\t"
        for song in self.songs:
            print(padding + song)

    def count_songs(self):
        return len(self.songs)

    def compare(self, other: 'AlbumDictTree'):
        """
        Returns a new AlbumDictTree containing songs present in this album but missing in the other.
        :param other:
        :return:
        """
        missing_songs = AlbumDictTree(self.title)
        for song_name in self.songs:
            song = self[song_name]
            if other.get(song.title) is None:
                missing_songs.add_song(song, set_title=True)
        return missing_songs

    def csv(self):
        rows = []
        for song in self.songs:
            song = self.songs[song]
            rows.append(song.csv())
        return rows


class Song:
    def __init__(self, path: str, title: str = "", album: str = "", artist: str = ""):
        self.title = str(title)
        self.path = path
        self.filetype = get_filetype(self.path)
        self.album = album
        self.artist = artist
        self.tags = self.get_tags()

    def get_tags(self):
        file = tl.File(self.path)
        return file.tags

    def show(self, prefix: str = ''):
        print(prefix + self.title)

    def csv(self):
        return [self.artist, self.album, self.title]


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
            song.show(prefix=padding)

    def count_songs(self):
        return len(self.songs)

    def all_filetypes(self):
        filetypes = []
        for song in self.songs:
            if song.filetype not in filetypes:
                filetypes.append(song.filetype)
        return filetypes
