import os
import taglib as tl
import csv
import shutil
from utils import *

song_filetypes = ['mp3', 'm4a', 'm4p', 'MP3', 'aif', 'm4v', 'Mp3', 'wav', 'mpg']
library_types = ['itunes', 'google play music', 'takeout', 'comparison', 'takeout csv']
empty_lists = [None, [], [""]]

# def playlist_takeout_to_itunes(path):


class SongDictTree:
    def __init__(self, path: str = None, library_type: str = 'Google Play Music', delete_duplicate: bool = False,
                 sort_files: bool = False, recurse: bool = True, populate: bool = True):
        """

        :param path: This should be the high-level directory in which the folders named after artists are contained.
        """
        self.num_tracks = 0
        self.artists = {}
        if library_type.lower() in library_types:
            self.type = library_type.lower()
        else:
            raise ValueError("Only library types ", library_types, "accepted.")

        if path is not None:
            self.path = check_trailing_slash(path)
            if populate:
                self.populate(delete_duplicate=delete_duplicate, sort_files=sort_files, recurse=recurse)
                if sort_files:
                    clear_empty_paths(path=path)
        else:
            self.path = None

        self.count_songs()

    def __getitem__(self, item):
        return self.artists[item]

    def __setitem__(self, key, value):
        self.artists[key] = value

    def get(self, item):
        return self.artists.get(item)

    def populate(self, delete_duplicate: bool = False, sort_files: bool = False, recurse: bool = True):
        if self.type == 'takeout csv':
            is_csv = True
        else:
            is_csv = False
        print('Building tree...')
        self.add_directory(path=self.path, recurse=recurse, delete_duplicate=delete_duplicate, sort_files=sort_files,
                           is_csv=is_csv)
        print('Done.')

    def add_directory(self, path, recurse: bool = False, delete_duplicate: bool = False, sort_files: bool = False,
                      is_csv: bool = False):
        path = check_trailing_slash(path)
        print('Adding directory:', path)
        if recurse:
            for directory in filter(lambda n: os.path.isdir(path + n), os.listdir(path)):
                self.add_directory(path=path + directory, recurse=True, delete_duplicate=delete_duplicate,
                                   sort_files=sort_files, is_csv=is_csv)

        if is_csv:
            allowed = ['csv']
        else:
            allowed = song_filetypes

        for song in filter(lambda f: get_filetype(f) in allowed, os.listdir(path)):
            self.add_song(path=path, filename=song, delete_duplicate=delete_duplicate, sort_files=sort_files,
                          is_csv=is_csv)

    def add_song(self, path: str, filename: str, delete_duplicate: bool = False, sort_files: bool = False,
                 is_csv: bool = False):
        print('Adding song:', path + "\\" + filename)
        path = check_trailing_slash(path) + filename
        song = Song(path, is_csv=is_csv)

        if song.tags.get('ARTIST') in [None, [], [""]]:
            if song.tags.get('ALBUMARTIST') in [None, [], [""]]:
                artist = 'None'
            else:
                artist = song.tags['ALBUMARTIST'][0]
        else:
            artist = song.tags['ARTIST'][0]
        song.artist = artist
        if self.artists.get(artist) is None:
            self.artists[artist] = ArtistDictTree(title=artist, sort_files=sort_files,
                                                  path=self.path)
        self.artists[artist].add_song(song, path=path, filename=filename, delete_duplicate=delete_duplicate,
                                      sort_files=sort_files)

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
        self.num_tracks = num
        return num

    def compare(self, other: 'SongDictTree', copy: bool = False):
        """
        Returns a new SongDictTree containing the artists present in this tree but missing in the other, etc.
        :param other:
        :return:
        """
        if copy:
            path = other.path
            sort_files = True
        else:
            path = None
            sort_files = False
        missing_artists = SongDictTree(library_type='comparison', path=path, sort_files=sort_files, populate=False)
        for artist_name in self.artists:
            artist = self.artists[artist_name]
            print("Searching for artist", artist.title)
            if other.get(artist.title) is None:
                print("Artist not found. Adding to difference. Copy is", copy)
                missing_artists[artist.title] = artist.__copy__(path=other.path, sort_files=copy)
            else:
                print("Artist found. Looking for missing albums.")
                missing_albums = artist.compare(other[artist.title], copy=copy)
                if len(missing_albums) > 0:
                    missing_artists[artist.title] = missing_albums
        missing_artists.count_songs()
        return missing_artists

    def csv(self):
        rows = []
        for artist in self.artists:
            artist = self.artists[artist]
            rows.extend(artist.csv())
        return rows

    def write_csv(self, path):
        path += '_' + str(self.num_tracks)
        if path[-4:] != '.csv':
            path += '.csv'
        rows = self.csv()
        rows.sort(key=lambda r: (r[0], r[1]))
        header = ['Artist', 'Album', 'Title', 'Path']
        # writing to csv file
        with open(path, 'w', newline='', encoding="utf-8") as csv_file:
            # creating a csv writer object
            csv_writer = csv.writer(csv_file)
            # writing the fields
            csv_writer.writerow(header)
            # writing the data rows
            csv_writer.writerows(rows)


class ArtistDictTree:
    def __init__(self, title: str, path: str = "", sort_files: bool = False):
        """
        :param title:
        :param path: The directory containing the albums by a certain artist.
        """
        self.title = str(title)
        self.path = check_trailing_slash(path)
        self.albums = {}
        if sort_files:
            if not os.path.isdir(path):
                os.mkdir(path)

    def __getitem__(self, item):
        return self.albums[item]

    def __setitem__(self, key, value):
        self.albums[key] = value

    def __len__(self):
        return len(self.albums)

    def __copy__(self, path: str = None, sort_files: bool = False):
        if path is None:
            path = self.path
        else:
            path = check_trailing_slash(path)

        copy = ArtistDictTree(title=self.title, path=path, sort_files=sort_files)
        for album_name in self.albums:
            copy.albums[album_name] = self.albums[album_name].__copy__(path=path + sanitise_path(album_name),
                                                                       sort_files=sort_files)
        return copy

    def get(self, item):
        return self.albums.get(item)

    def add_song(self, song: 'Song', path: str, filename: str, delete_duplicate: bool = False,
                 sort_files: bool = False):
        if song.tags.get('ALBUM') in [None, [], [""]]:
            album = 'None'
        else:
            album = song.tags['ALBUM'][0]
        song.album = album
        if self.get(album) is None:
            self[album] = AlbumDictTree(title=album, artist=self.title, sort_files=sort_files,
                                        path=self.path + sanitise_path(album))
        self.albums[album].add_song(song, path=path, filename=filename, delete_duplicate=delete_duplicate,
                                    sort_files=sort_files)

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

    def compare(self, other: 'ArtistDictTree', copy: bool = False):
        """
        Returns a new ArtistDictTree containing the albums present in this artist but missing in the other; it will also
        include albums present in both but missing songs in the other, with those songs listed.
        :param other:
        :return:
        """
        missing_albums = ArtistDictTree(self.title, path=other.path, sort_files=copy)
        for album_name in self.albums:
            album = self[album_name]
            print("\tSearching for album", album.title, "in", self.title)
            if other.get(album.title) is None:
                print("\tAlbum not found. Adding to difference. Copy is", copy)
                missing_albums[album.title] = album.__copy__(path=other.path + sanitise_path(album.title),
                                                             sort_files=copy)
                # for song_name in album.songs:
                #     song = album.songs[song_name]
                #     print("\t\tAdding", song_name, "to difference. Copy is", copy)
                #     missing_albums[album.title].add_song(song=song, path=song.path, sort_files=copy, move=False)
            else:
                print("\tAlbum found. Looking for missing songs. Copy is", copy)
                missing_songs = album.compare(other[album.title], copy=copy)
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
    def __init__(self, title: str, artist: str = "", path: str = "", sort_files: bool = False):
        """

        :param title:
        :param path: The directory containing the songs of an album.
        """
        self.title = str(title)
        self.path = check_trailing_slash(path)
        self.artist = artist
        self.songs = {}

        if sort_files:
            if not os.path.isdir(path):
                os.mkdir(path)

    def __getitem__(self, item):
        return self.songs[item]

    def __setitem__(self, key, value):
        self.songs[key] = value

    def __len__(self):
        return len(self.songs)

    def __copy__(self, path: str = None, sort_files: bool = False):
        if path is None:
            path = self.path
        else:
            path = check_trailing_slash(path)
        copy = AlbumDictTree(title=self.title, artist=self.artist, path=path, sort_files=sort_files)
        for song_name in self.songs:
            song = self.songs[song_name]
            copy.add_song(song=song, path=song.path, sort_files=sort_files)
        return copy

    def get(self, item):
        return self.songs.get(item)

    def add_song(self, song: 'Song', path: str = '', filename: str = '', set_title: bool = True,
                 delete_duplicate: bool = False, sort_files: bool = False, move: bool = True):
        if filename == '':
            filename = get_filename(path)

        if set_title:
            if song.tags.get('TITLE') in [None, [], [""]]:
                title = filename
            else:
                title = song.tags['TITLE'][0]
            song.title = title
        if self.get(song.title) is None:
            self[song.title] = song
            if sort_files:
                new_path = self.path + filename
                if new_path != path:
                    song.path = new_path
                    if move:
                        print("Moving", path, "to", new_path)
                        shutil.move(src=path, dst=new_path)
                    else:
                        print("Copying", path, "to", new_path)
                        shutil.copy(src=path, dst=new_path)

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

    def compare(self, other: 'AlbumDictTree', copy: bool = False):
        """
        Returns a new AlbumDictTree containing songs present in this album but missing in the other.
        :param other:
        :return:
        """
        # sort_files is copy because, if we are copying, it needs to create/check for the destination folder's exisence.
        missing_songs = AlbumDictTree(self.title, path=other.path, sort_files=copy)
        for song_name in self.songs:
            song = self[song_name]
            print("\t\tSearching for song", song.title, "in", other.title)
            if other.get(song.title) is None:
                print("\t\tSong not found. Adding to difference. Copy is", copy)
                missing_songs.add_song(song, path=song.path, set_title=True, sort_files=copy, move=False)
            else:
                print("\t\tSong found. Ignoring.")
        return missing_songs

    def csv(self):
        rows = []
        for song in self.songs:
            song = self.songs[song]
            rows.append(song.csv())
        return rows


class Song:
    def __init__(self, path: str, title: str = "", album: str = "", artist: str = "", is_csv: bool = False):
        self.title = str(title)
        self.path = path
        self.filetype = get_filetype(self.path)
        self.album = album
        self.artist = artist
        self.is_csv = is_csv
        self.tags = self.get_tags()

    def get_tags(self):
        if self.is_csv:
            # try:
            with open(self.path, newline='', encoding="utf8") as csvfile:
                reader = csv.DictReader(csvfile)

                csv_row = reader.__next__()
            tags = {'TITLE': [csv_row['Title']],
                    'ALBUM': [csv_row['Album']],
                    'ARTIST': [csv_row['Artist']],
                    'ALBUMARTIST': [csv_row['Artist']]}
            # except UnicodeDecodeError:
            #     tags = {'TITLE': 'ERROR',
            #             'ALBUM': 'ERROR',
            #             'ARTIST': 'ERROR',
            #             'ALBUMARTIST': 'ERROR'}
            return tags
        else:
            file = tl.File(self.path)
            return file.tags

    def show(self, prefix: str = ''):
        print(prefix + self.title)

    def csv(self):
        return [self.artist, self.album, self.title, self.path]
