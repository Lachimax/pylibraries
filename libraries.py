import pandas as pd

# TODO: Average rating by series

class GameLibrary:
    def __init__(self, path=None):
        self.games = list()

        self.unique_game_count = 0
        self.unique_dlc_count = 0

        if path is not None:
            self.import_from_xl(path)

    def __getitem__(self, item):
        return self.games[item]

    def show(self, sort='title', dlc=False, unique=True):

        if sort == 'title':
            self.games.sort(key=lambda g: g.title.lower())

            for g in self:
                print(g.title)

                if dlc:
                    for i in g.includes:
                        print('    Includes: ' + i.title)
                    for d in g.dlc:
                        print('    DLC: ' + d.title)

        if sort == 'developer':

            self.games.sort(key=lambda g: g.developer)

            for g in self.games:
                print(g.title + ': ' + str(g.developer.lower()))

                if dlc:
                    for i in g.includes:
                        print('    Includes: ' + i.title)
                    for d in g.dlc:
                        print('    DLC: ' + d.title)

        if sort == 'metacritic':

            self.games.sort(key=lambda g: g.metacritic)

            for g in self.games:
                print(g.title + ': ' + str(g.metacritic))

                if dlc:
                    for i in g.includes:
                        print('    Includes: ' + i.title + ': ' + i.metacritic)
                    for d in g.dlc:
                        print('    DLC: ' + d.title + ': ' + d.metacritic)

    def count_unique(self):
        '''
        :param num:
        :return:
        '''

        games = list()
        dlcs = list()

        for game in self:

            g = TitleNum(game.instance_of, 0)

            if g.title != 'nan':

                if g not in games:
                    games.append(g)
                    self.unique_game_count += 1

                if game.dlc:

                    for dlc in game.dlc:
                        d = TitleNum(dlc.title, 1)

                        if d not in dlcs and d.title != 'nan':
                            dlcs.append(d)
                            self.unique_dlc_count += 1

                if game.includes:

                    for include in game.includes:
                        inc = TitleNum(include.instance_of, 1)

                        if inc not in games:
                            games.append(inc)
                            self.unique_game_count += 1

        print('Number of Unique Games: ' + str(self.unique_game_count))
        print('Number of Unique DLCs: ' + str(self.unique_dlc_count))
        return dlcs

    def most_owned_series(self, num=10):
        '''
        Does not count DLC or included games.
        :param num:
        :return:
        '''

        games = list()

        for game in self:

            g = TitleNum(game.series, 1)

            if g.title != 'nan':

                if g not in games:
                    games.append(g)

                else:
                    i = games.index(g)
                    games[i].increment()

        games.sort(key=lambda t: t.num, reverse=True)

        for i in range(num):
            print(str(i) + '. ' + str(games[i].title) + ' (' + str(games[i].num) + ')')

        print()

    def most_owned(self, num=10):
        '''
        DOES count DLC and included games, but only when they are full games.
        :param num:
        :return:
        '''

        games = list()

        for game in self:

            g = TitleNum(game.instance_of, 1)

            # Don't count the nans
            if g.title != 'nan':

                if g not in games:
                    games.append(g)

                else:
                    i = games.index(g)
                    games[i].increment()

                if game.dlc:

                    for dlc in game.dlc:
                        d = TitleNum(dlc.instance_of, 1)

                        if d.title != 'nan':

                            if d not in games:
                                games.append(d)

                            else:
                                i = games.index(d)
                                games[i].increment()

                if game.includes:

                    for include in game.includes:
                        inc = TitleNum(include.instance_of, 1)

                        if inc.title != 'nan':

                            if inc not in games:
                                games.append(inc)

                            else:
                                i = games.index(inc)
                                games[i].increment()

        games.sort(key=lambda t: t.num, reverse=True)

        for i in range(num):
            print(str(i) + '. ' + str(games[i].title) + ' (' + str(games[i].num) + ')')

        print()

    def count_libraries(self):
        libraries = list()

        for game in self:
            l = TitleNum(game.platform, 1)

            # Don't count the nans
            if l.title != 'nan':

                if l not in libraries:
                    libraries.append(l)

                else:
                    i = libraries.index(l)
                    libraries[i].increment()

        libraries.sort(key=lambda lib: lib.num, reverse=True)

        for i, l in enumerate(libraries):
            print(str(i) + ". " + str(l.title) + " (" + str(l.num) + ")")
        print()

    def count_formats(self):
        formats = list()

        for game in self:
            f = TitleNum(game.formats, 1)

            # Don't count the nans
            if f.title != 'nan':

                if f not in formats:
                    formats.append(f)

                else:
                    i = formats.index(f)
                    formats[i].increment()

        formats.sort(key=lambda lib: lib.num, reverse=True)

        for i, f in enumerate(formats):
            print(str(i) + ". " + str(f.title) + " (" + str(f.num) + ")")
        print()

    def completion_stats(self):
        completion_levels = list()

        for game in self:
            c = TitleNum(game.completion, 1)

            # Don't count the nans
            if c.title != 'nan':

                if c not in completion_levels:
                    completion_levels.append(c)

                else:
                    i = completion_levels.index(c)
                    completion_levels[i].increment()

        completion_levels.sort(key=lambda lib: lib.num, reverse=True)

        for i, c in enumerate(completion_levels):
            percent = 100*(c.num/self.unique_game_count)
            print(str(i) + ". " + str(c.title) + " (" + str(c.num) + ")" + "[" + str(percent) + "%]")

        print()


    def import_from_xl(self, path="C:\\Users\\Lachlan\\Google Drive\\Projects\\Python\\libraries\\Games Library.xlsx"):
        lib = pd.read_excel(path)
        lib = lib.as_matrix()
        lib = lib[4:]

        for i in range(len(lib)):

            row = lib[i]

            if ' + ' not in str(row[0]) and ' ^ ' not in str(row[0]):

                game = Game()
                game.title = str(row[0])
                game.instance_of = str(row[1])
                game.platform = str(row[2])
                game.formats = str(row[3])
                game.series = str(row[4])
                game.series_num = str(row[5])
                game.developer = str(row[6])
                game.publisher = str(row[7])
                game.local_players = str(row[8])
                game.online_players = str(row[9])
                game.release_date = str(row[10])
                game.obtained = str(row[11])
                game.completion = str(row[12])
                game.metacritic = str(row[13])
                if 'nan' in game.metacritic:
                    game.metacritic = '0.0'
                game.gamerankings = str(row[14])
                game.my_rating = str(row[15])
                game.condition = str(row[16])
                if row[17] == 'nan' or row[17] == 'N':
                    game.box = False
                elif row[17] == 'Y':
                    game.box = True
                if row[18] == 'nan' or row[18] == 'N':
                    game.manual = False
                elif game.manual == 'Y':
                    game.manual = True
                game.other = str(row[19])
                game.gb_notes = str(row[20])
                game.key = str(row[21])
                game.generation = float(row[22])

                if i < len(lib) - 1:

                    j = i + 1

                    while ' + ' in str(lib[j][0]) or ' ^ ' in str(lib[j][0]):

                        row_n = lib[j]

                        if ' + ' in row_n[0]:

                            dlc = Game()

                            dlc = Game()
                            dlc.title = row_n[0].replace('   + ', '')
                            dlc.instance_of = row_n[1]
                            dlc.platform = row_n[2]
                            dlc.formats = row_n[3]
                            dlc.series = row_n[4]
                            dlc.series_num = row_n[5]
                            dlc.developer = row_n[6]
                            dlc.publisher = row_n[7]
                            dlc.local_players = row_n[8]
                            dlc.online_players = row_n[9]
                            dlc.release_date = row_n[10]
                            dlc.obtained = row_n[11]
                            dlc.completion = row_n[12]
                            dlc.metacritic = str(row_n[13])
                            dlc.gamerankings = str(row_n[14])
                            dlc.my_rating = str(row_n[15])
                            dlc.condition = row_n[16]
                            if row_n[17] == 'nan' or row_n[17] == 'N':
                                dlc.box = False
                            elif row_n[17] == 'Y':
                                dlc.box = True
                            if row_n[18] == 'nan' or row_n[18] == 'N':
                                dlc.manual = False
                            elif dlc.manual == 'Y':
                                dlc.manual = True
                            dlc.other = row_n[19]
                            dlc.gb_notes = row_n[20]
                            dlc.key = row_n[21]
                            dlc.generation = float(row_n[22])

                            game.dlc.append(dlc)


                        else:

                            include = Game()

                            include = Game()
                            include.title = row_n[0].replace('   ^ ', '')
                            include.instance_of = row_n[1]
                            include.platform = row_n[2]
                            include.formats = row_n[3]
                            include.series = row_n[4]
                            include.series_num = row_n[5]
                            include.developer = row_n[6]
                            include.publisher = row_n[7]
                            include.local_players = row_n[8]
                            include.online_players = row_n[9]
                            include.release_date = row_n[10]
                            include.obtained = row_n[11]
                            include.completion = row_n[12]
                            include.metacritic = float(row_n[13])
                            include.gamerankings = float(row_n[14])
                            include.my_rating = float(row_n[15])
                            include.condition = row_n[16]
                            if row_n[17] == 'nan' or row_n[17] == 'N':
                                include.box = False
                            elif row_n[17] == 'Y':
                                include.box = True
                            if row_n[18] == 'nan' or row_n[18] == 'N':
                                include.manual = False
                            elif include.manual == 'Y':
                                include.manual = True
                            include.other = row_n[19]
                            include.gb_notes = row_n[20]
                            include.key = row_n[21]
                            include.generation = float(row_n[22])

                            game.includes.append(include)

                        j += 1

                self.games.append(game)


class Game:
    def __init__(self):
        self.title = str()
        self.instance_of = str()
        self.platform = str()
        self.formats = str()
        self.series = str()
        self.series_num = str()
        self.developer = str()
        self.publisher = str()
        self.local_players = str()
        self.online_players = str()
        self.release_date = str()
        self.obtained = str()
        self.completion = str()
        self.metacritic = float()
        self.gamerankings = float()
        self.my_rating = float()
        self.condition = str()
        self.box = False
        self.manual = False
        self.other = str()
        self.gb_notes = str()
        self.key = str()
        self.generation = float()
        self.includes = list()
        self.dlc = list()


class Completion:
    def __init__(self, case='Unplayed'):
        if case == 'Unplayed':
            self.case = 'Unplayed'
        elif case == 'Played':
            self.case = 'Played'
        elif case == 'Finished':
            self.case = 'Finished'
        elif case == 'Complete':
            self.case = 'Complete'
        else:
            raise ValueError('Case not recognised')

    def __str__(self):
        return self.case


class TitleNum:
    def __init__(self, title, num=0):
        self.title = str(title)
        self.num = num

    def __eq__(self, other):
        if self.title == other.title:
            return True
        else:
            return False

    def increment(self):
        self.num += 1
