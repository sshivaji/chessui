import json
import logging
import os
import time

import re
import tornado
import chess

from external import scoutfish
from external import chess_db
from handlers.basic_handler import BasicHandler
from tornado.escape import json_encode
from tornado.ioloop import IOLoop
from tornado.web import asynchronous
from models import game_database as game_db
from peewee import *

import logging
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

SCOUTFISH_EXEC = './external/scoutfish'
CHESSDB_EXEC = './external/parser'
MILLIONBASE_PGN = './bases/millionbase.pgn'
MILLIONBASE_SQLITE = './bases/millionbase.sqlite'

SQLITE_GAME_LIMIT = 990

GAME_UI_DB = {
    "White": "white",
    "WhiteElo": "white_elo",
    "Black": "black",
    "BlackElo": "black_elo",
    "Result": "result",
    "Date": "date",
    "Event": "event",
    "Site": "site"
}


class SortKey(object):
    def __init__(self, name, direction):
        self.name = name
        self.direction = direction

    def __repr__(self):
        return 'Name : {0}, Direction: {1}'.format(self.name, self.direction)


class ChessBoardHandler(BasicHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self):
        self.render('../web/templates/board2.html')


class ChessQueryHandler(BasicHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def process_results(self, results, callback):
        if callback:
            jsonp = "{jsfunc}({json});".format(jsfunc=callback,
                                               json=json_encode(results))
            self.set_header('Content-Type', 'application/javascript')
            self.write(jsonp)
        else:
            self.write(results)
        # self.finish()

    def get(self):
        ## This is created on server init
        if 'chessDB' not in self.shared:
            self.chessDB = chess_db.Parser(CHESSDB_EXEC)
            self.shared['chessDB'] = self.chessDB
            # print("Creating chessDB in shared")
        else:
            self.chessDB = self.shared['chessDB']

        ## This is created on server init
        if 'scoutfish' not in self.shared:
            self.scoutfish = scoutfish.Scoutfish(SCOUTFISH_EXEC)
            self.shared['scoutfish'] = self.scoutfish
        else:
            self.scoutfish = self.shared['scoutfish']

        # moves = self.get_arguments("moves")
        # print self.get_argument("sorts")
        action = self.get_argument("action", default=None)
        requested_db = self.get_argument("db", default=None)
        if not action:
            logging.info("No action sent")
            return
            # self.finish()

        logging.info("requested_db: {0}".format(requested_db))

        # Assign fen to self as the self object is recreated every request anyway and it simplifies the callback mechanism
        fen = self.get_argument("fen", default=None)
        logging.info("fen : {0}".format(fen))
        callback = self.get_argument('callback', default='')

        # TODO: Use thread pool to process slower queries
        results = self.process_request(action, fen)
        self.process_results(results, callback)

    def query_sql_data(self, db, game_ids=None, order_by_list=None, page_number=None, items_per_page=None,
                       search_terms=None):

        sqlite_db = SqliteDatabase(db)

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
                database = sqlite_db

                # def __str__(self):
                #     return "White: {0}, white_elo: {1}, black: {2}, black_elo: {3}, result: {4}, date: {5}, event: {6}, site: {7}, " \
                #            "eco: {8}".format(white, white_elo, black, black_elo, result, date, event, site, eco)
                #

            def as_dict(self):
                return {
                    'offset': self.offset,
                    'offset_8': self.offset_8,
                    'white': self.white,
                    'white_elo': self.white_elo,
                    'black': self.black,
                    'black_elo': self.black_elo,
                    'result': self.result,
                    'date': self.date,
                    'event': self.event,
                    'site': self.site,
                    'eco': self.eco,
                }

        query = Game.select()

        if search_terms:
            for t in search_terms:
                if t == '1-0' or t == '1/2-1/2' or t == '0-1':
                    query = query.where(Game.result == t)
                elif t.isdigit():
                    # print "digit"
                    # print t
                    num = int(t)
                    if num < 2050:
                        # Its a year
                        query = query.where(Game.date ** ('%%%s%%' % (t)))
                else:
                    query = query.where((Game.black ** ('%%%s%%' % (t)) | Game.white ** ('%%%s%%' % (t))))
                    # query = query.where(getattr(Game, 'white') ** ('%%%s%%' % ('Carlsen')))
                    # query = query.where(getattr(Game, 'white') == ('%%%s%%' % ('Carlsen')))

                    # query = query.where((Game.black ** ('%%%s%%' % (t))) | (Game.white ** ('%%%s%%' % (t))))
                    # query = query.where(Game.black ** ('%%%s%%' % (t)))

        if 1 <= len(game_ids) <= SQLITE_GAME_LIMIT:
            query = query.where(getattr(Game, 'offset_8') << game_ids)

        if order_by_list:
            # Construct peewee order by clause
            order_by_cond = []
            for sort_key in order_by_list:
                if sort_key.direction > 0:
                    order_by_cond.append(getattr(Game, GAME_UI_DB[sort_key.name]).asc())
                else:
                    order_by_cond.append(getattr(Game, GAME_UI_DB[sort_key.name]).desc())

            query = query.order_by(*order_by_cond)
            # getattr(Game,'black_elo').asc(), getattr(Game,'eco').asc()
        if page_number and items_per_page:
            query = query.paginate(page_number, items_per_page)
        else:
            print("no page number")

        # print(query.desc)
        # query = query.limit(10)

        # query = query.execute()

        # results = [p for p in query]
        # results = []
        # print("results: {}".format(results))
        # for r in results:
        #     print("{0} {1} - {2} {3} {4} {5} {6}".format(r.white, r.white_elo, r.black, r.black_elo, r.result, r.date, r.eco))
        # print r.black

        return [p for p in query]

    def process_request(self, action, fen):
        # records = []
        sql_results = {}
        if action == "get_book_moves":
            # logging.info("get book moves :: ")
            records = self.query_db(fen)

            # Reverse sort by the number of games and select the top 5, otherwise all odd moves will show up..
            records.sort(key=lambda x: x['games'], reverse=True)
            sql_results = {"records": records[:5]}

        elif action == "get_games":
            # perPage = 20 & page = 2 & offset = 20
            perPage = self.get_argument("perPage", default=10)
            perPage = int(perPage)
            # page = self.get_argument("page", default=1)
            offset = self.get_argument("offset", default=0)
            offset = int(offset)

            print("perPage: {0}, offset: {1}".format(perPage, offset))

            # convert to skip and limit logic
            # offset = skip
            # limit = perPage

            sort_list = []
            search_terms = []
            order_expr = {}
            columns = {}
            for k, v in self.request.arguments.iteritems():
                if k.startswith('sorts['):
                    m = re.findall('sorts\[(.*?)\]', k, re.DOTALL)
                    sort_key = m[0]
                    direction = int(v[0])
                    # Perform a reverse sort for date or elo (ascending is less useful)
                    if 'elo' in sort_key or 'date' in sort_key:
                        direction *= -1
                    sort_list.append(SortKey(sort_key, direction))
                    # 'queries[search]'
                if k.startswith('queries['):
                    m = re.findall('queries\[(.*?)\]', k, re.DOTALL)
                    if ' ' in v[0]:
                        search_terms = v[0].split()
                    else:
                        search_terms = [v[0]]
                # 'search[value]'
                if k.startswith('search['):
                    m = re.findall('search\[(.*?)\]', k, re.DOTALL)
                    if m[0] == 'value' and v[0]:
                        if ' ' in v[0]:
                            search_terms = v[0].split()
                        else:
                            search_terms = [v[0]]

                if k.startswith('columns['):
                    m = re.findall('columns\[(.*?)\]\[(.*?)\]', k, re.DOTALL)
                    num, col = m[0]
                    if col == 'data':
                        columns[num] = v[0]

                if k.startswith('order['):
                    m = re.findall('order\[(.*?)\]\[(.*?)\]', k, re.DOTALL)
                    num, col = m[0]
                    num = int(num)
                    val = v[0] if col == 'column' else 1 if v[0] == 'asc' else -1
                    if num not in order_expr:
                        order_expr[num] = {}
                    order_expr[num][col] = val
            print("search terms: {}".format(search_terms))
            # print("search terms: {}".format(search_terms))
            print ("order_expr: {}".format(order_expr))

            for k in order_expr:
                sort_key = columns[order_expr[k]['column']]
                sort_list.append(SortKey(sort_key, order_expr[k]['dir']))

            print("Sort_list: {}".format(sort_list))

            records = self.query_db(fen, skip=offset, limit=perPage)
            # print("records: {}".format(records))
            # Reverse sort by the number of games and select the top 5, for a balanced representation of the games
            records.sort(key=lambda x: x['games'], reverse=True)
            # For reporting purposes
            total_result_count = sum(r['games'] for r in records)
            print("total_result_count: {}".format(total_result_count))
            # print("records: {}".format(records))

            filtered_records = records[:5]
            filtered_game_offsets = []
            # Limit number of games to 10 for now
            game_ids = []
            # for r in records:
            #     total_result_count += r['games']
            for r in records:
                game_ids.extend(r['pgn offsets'])

            # print("game_ids: {}".format(game_ids))
            print("len (game_ids): {}".format(len(game_ids)))
            # total_result_count = len(game_ids)

            for r in filtered_records:
                for of in r['pgn offsets']:
                    # print("offset: {0}".format(offset))
                    if len(filtered_game_offsets) >= perPage:
                        break
                    filtered_game_offsets.append(of)
                    # else:
                    #     break
                    # total_result_count += 1
            print("total_result_count: {}".format(total_result_count))
            print("len_search terms: {}".format(len(search_terms)))
            if (len(search_terms) > 0) and total_result_count > SQLITE_GAME_LIMIT:
                # print("In search terms block")
                # Some balancing to remove searched games not from the position given sqlite limit of 999 for the in clause
                # If applying search term on more than 999 sql_results, chances are, the paging does not have to be exact
                game_ids = []
                # _result_id_set = set()
                sql_results = self.query_sql_data(MILLIONBASE_SQLITE, game_ids=[], order_by_list=sort_list,
                                              search_terms=search_terms)
                large_records = self.query_db(fen, limit=3000000)
                for r in large_records:
                    game_ids.extend(r['pgn offsets'])

                game_id_set = set(game_ids)


                intersection = [g.offset for g in sql_results if g.offset in game_id_set]

                filtered_game_offsets = intersection[offset:offset+perPage]
                print("offset: {}".format(offset))
                print("offset+perpage: {}".format(offset+perPage))

                print("filtered_game_offsets after pagination: {}".format(filtered_game_offsets))
                total_result_count = len(intersection)


            print("filtered_game_offset count : {0}".format(len(filtered_game_offsets)))
            headers = self.chessDB.get_game_headers(self.chessDB.get_games(filtered_game_offsets))


            # tag the offset to each header
            for offset, h in zip(filtered_game_offsets, headers):
                # Should be sent as ID for front end accounting purposes, in an odd way, the offset is the game id,
                # as its the unique way to access the game
                h["id"] = offset

            sql_results = {"records": headers, "queryRecordCount": total_result_count,
                       "totalRecordCount": total_result_count}

        elif action == "get_game_content":
            game_offset = self.get_argument("game_offset", default=0)
            game_offset = int(game_offset)
            if game_offset:
                # Get first result as its just one game
                pgn = self.chessDB.get_games([game_offset])[0]
                # Split it up again as we need one line at a time for the frontend to parse it correctly
                sql_results = {"pgn": pgn.split(os.linesep)}
        return sql_results

    def query_db(self, fen, limit = 100, skip = 0):
        records = []
        # selecting DB happens now
        self.chessDB.open(MILLIONBASE_PGN)
        results = self.chessDB.find_large(fen, limit=limit, skip=skip)
        board = chess.Board(fen)
        for m in results['moves']:
            # print(m)
            m['san'] = board.san(chess.Move.from_uci(m['move']))
            record = {'move': m['san'], 'pct': "{0:.2f}".format(
                (m['wins'] + m['draws'] * 0.5) * 100.0 / (m['wins'] + m['draws'] + m['losses'])), 'freq': m['games'],
                      'wins': m['wins'],
                      'draws': m['draws'], 'losses': m['losses'], 'games': int(m['games']), 'pgn offsets': m['pgn offsets']}
            records.append(record)
        return records