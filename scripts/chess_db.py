from peewee import *
import argparse
import csv
import cjson as json
import operator
import os

INDEX_TOTAL_GAME_COUNT = "total_game_count"
SQLITE_GAME_LIMIT = 990
INDEX_FILE_POS = "last_pos"

DB_HEADER_MAP = {"White": 0, "WhiteElo": 1, "Black": 2,
                 "BlackElo": 3, "Result": 4, "Date": 5, "Event": 6, "Site": 7,
                 "ECO": 8, INDEX_FILE_POS: 9, "FEN": 10, "PlyCount": 11, "EventDate": 12, "EventType": 13}

# FRONTEND_TO_BACKEND_ATTR_MAP = {'White': 'white', 'White Elo'}

def get_operator_fn(op):
    return {
        '+' : operator.add,
        '-' : operator.sub,
        '*' : operator.mul,
        '/' : operator.div,
        '%' : operator.mod,
        '^' : operator.xor,
        '>' : operator.gt,
        '<' : operator.lt,
        }[op]

#
# def get_game(db_index, game_num):
#     # db_index = self.ref_db_index_book
#     print (db_index.Get("game_0_data", regular=True))
#     first = db_index.Get("game_{0}_data".format(game_num), regular=True).split("|")[DB_HEADER_MAP[INDEX_FILE_POS]]
#     #        if game_num+1 < self.pgn_index[INDEX_TOTAL_GAME_COUNT]:
#     #            second = self.db_index_book.Get("game_{0}_{1}".format(game_num+1,INDEX_FILE_POS))
#     #        second = self.pgn_index["game_index_{0}".format(game_num+1)][INDEX_FILE_POS]
#     try:
#         second = db_index.Get("game_{0}_data".format(game_num + 1), regular=True).split("|")[DB_HEADER_MAP[INDEX_FILE_POS]]
#         second = int(second)
#     except KeyError:
#         second = None
#
#     file_name = db_index.Get("pgn_filename", regular=True)
#     if not os.path.isfile(file_name):
#         file_name = file_name.replace("home", "Users")
#
#     with open(file_name) as f:
#         first = int(first)
#
#         f.seek(first)
#         line = 1
#         lines = []
#         first_line = False
#         while line:
#             line = f.readline()
#             temp = line.strip()
#             if not first_line:
#                 temp = '[' + temp
#             first_line = True
#             # line = line.strip()
#             pos = f.tell()
#             if second and pos >= second:
#                 break
#                 # print pos
#             if temp:
#                 lines.append(temp)
#         # f.close()
#     # print lines
#     return lines

def query_data(game, game_ids=None, order_by_list=None, limit=10, page_number=None, items_per_page=None,
                   search_terms=None):
        query = game.select()
        # query = query.where(Game.black ** ('%%%s%%' % ('Carlsen')) | Game.white ** ('%%%s%%' % ('Carlsen')))
        # print dir(Game)
        # print Game.
        query = query.where(getattr(Game,'white') ** ('%%%s%%' % ('Carlsen')))

        if search_terms:
            for t in search_terms:
                if '>' in t or '<' in t or '=' in t:
                    opr = '='
                    if '>' in t:
                        opr = '>'
                    if '<' in t:
                        opr = '<'

                    attr, value = t.split(opr)
                    query = query.where(get_operator_fn(opr)(getattr(game, attr), value))
                # elif t == '1-0' or t == '1/2-1/2' or t == '0-1':
                #     query = query.where(game.result == t)
                # elif t.isdigit():
                #     # print "digit"
                #     # print t
                #     num = int(t)
                #     if num < 2050:
                #         # Its a year
                #         query = query.where(game.date ** ('%%%s%%' % (t)))
                else:
                    query = query.where(game.black ** ('%%%s%%' % (t)) | game.white ** ('%%%s%%' % (t)))

        if game_ids and len(game_ids) <= SQLITE_GAME_LIMIT:
            query = query.where(getattr(game, 'id') << game_ids)

        if order_by_list:
            # Construct peewee order by clause
            order_by_cond = []
            for sort_key in order_by_list:
                if sort_key.direction > 0:
                    order_by_cond.append(getattr(game, sort_key.name).asc())
                else:
                    order_by_cond.append(getattr(game, sort_key.name).desc())

            query = query.order_by(*order_by_cond)
            # getattr(Game,'black_elo').asc(), getattr(Game,'eco').asc()
        if page_number and items_per_page:
            query = query.paginate(page_number, items_per_page)

        # query = query.limit(limit)

        results = [p for p in query]
        for r in results:
            print ("{0} {1} - {2} {3} {4} {5} {6}".format(r.white, r.white_elo, r.black, r.black_elo, r.result, r.date, r.eco))
        # print r.black
        return results


# def import_data_csv(out_file):
#     db_index = leveldb.LevelDB('../frontend/resources/polyglot_index.db')
#     # db.execute_sql("pragma synchronous = off;")
#     total_games = int(db_index.Get(INDEX_TOTAL_GAME_COUNT))
#     print "total_games: {0}".format(total_games)
#     # writer = csv.writer(open(out_file,'wb'), delimiter='|')
#
#     with open(out_file, 'wb') as csv_file:
#         writer = csv.writer(csv_file, delimiter='|')
#         writer.writerow(['white', 'white_elo', 'black', 'black_elo', 'result', 'date', 'event', 'site', 'eco', 'ply'])
#         for i in xrange(1, total_games-1):
#             try:
#
#                 headers = db_index.Get("game_{0}_data".format(i), regular=True).split("|")
#                 # print len(headers)
#                 row = headers[:9]
#                 row.append(headers[11])
#                 # print row
#                 writer.writerow(row)
#             except KeyError:
#                 print "error getting game {0}".format(i)
#             if i % 10000 == 0:
#                 print i
#             # if i>5:
#             #     break


def import_data(json_path):
    Game.create_table(fail_silently=True)

    # db_index = leveldb.LevelDB('../frontend/resources/polyglot_index.db')
    # db_index = PartitionedLevelDB('../frontend/resources/white.db')
    #leveldb_path = '../frontend/resources/paramount_2015.db'
    #pgn_path = '../frontend/resources/paramount_2015.pgn'

    if not os.path.exists(json_path):
        # command = "polyglot make-book -pgn '{0}' -leveldb '{1}' -min-game 1".format(pgn_path, leveldb_path)
        # print command
        # os.system(command)
        print("Need a JSON path")
    # db_index = PartitionedLevelDB(leveldb_path)

    # db.execute_sql("pragma synchronous = off;")
    # print db_index.Get(INDEX_TOTAL_GAME_COUNT)
    # total_games = int(db_index.Get(INDEX_TOTAL_GAME_COUNT, regular=True))
    # print "total_games: {0}".format(total_games)

    # headers = db_index.Get("game_{0}_data".format(g)).split("|")
    # records.append ({"White": headers[0], "WhiteElo": headers[1], "Black": headers[2],
    # "BlackElo": headers[3], "Result": headers[4], "Date": headers[5], "Event": headers[6], "Site": headers[7],
    # "ECO": headers[8]})
    # total_games-1
    num_games = 0
    batch = []
    with open(json_path) as fp:
        for i, line in enumerate(fp):
            # print(line)
            try:
                j = json.decode(line)
            except:
                print(line)
                raise
                # line = line.replace("\", "\\")
            try:
                g = Game()
                g.offset = j.get('offset', None)
                g.offset_8 = j.get('offset_8', None)

                g.white = j.get('White', None)
                g.white_elo = j.get('WhiteElo', 2400)

                g.black = j.get('Black', None)
                g.black_elo = j.get('BlackElo', 2400)
                g.result = j.get('Result', None)
                g.date = j.get('Date', None)
                g.event = j.get('Event', None)
                g.site = j.get('Site', None)
                g.eco = j.get('ECO', '')

                if g.white_elo == '*':
                    g.white_elo = 0

                if g.black_elo == '*':
                    g.black_elo = 0

                # batch.append(g)

                try:
                    # Game.create(g)
                    with db.atomic():
                        g.save()
                        # Game.create(g)
                        # Game.insert_many(batch).execute()
                        # print("num_games: {}".format(num_games))
                        # num_games+=1
                except ValueError:
                    # raise
                    print (g.white)
                    print (g.white_elo)
                    print (g.black)
                    print (g.black_elo)
                    print (g.result)
                    print (g.date)
                    print (g.event)
                    print (g.site)
                    print (g.eco)

                if i % 10000 == 0:
                    print (i)

            except KeyError:
                print ("error getting game {0}".format(i))




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', help='Input JSON path')
    parser.add_argument('-o', '--output_file', default='game.db', help='Output DB path')

    arg = parser.parse_args()
    db = SqliteDatabase(arg.output_file)


    class Game(Model):
        offset = IntegerField(primary_key=True)
        offset_8 = IntegerField(index=True)
        white = CharField(index=True)
        white_elo = IntegerField(index=True)
        black = CharField(index=True)
        black_elo = IntegerField(index=True)
        result = CharField(index=True)
        date = DateField(index=True)
        event = CharField(index=True)
        site = CharField(index=True)
        eco = CharField(index=True)

        class Meta:
            database = db

            # def __str__(self):
            #     return "White: {0}, white_elo: {1}, black: {2}, black_elo: {3}, result: {4}, date: {5}, event: {6}, site: {7}, " \
            #            "eco: {8}".format(white, white_elo, black, black_elo, result, date, event, site, eco)
            #

    import_data(arg.input_file)
    games = query_data(Game, limit=10)

