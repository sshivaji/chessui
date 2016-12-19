import json
import logging
import time
import tornado
import chess

from external import scoutfish
from external import chess_db
from handlers.basic_handler import BasicHandler
from tornado.escape import json_encode
from tornado.ioloop import IOLoop
from tornado.web import asynchronous
from multiprocessing.pool import ThreadPool

_workers = ThreadPool(5)

SCOUTFISH_EXEC = './external/scoutfish'
CHESSDB_EXEC = './external/parser'
MILLIONBASE_PGN = './bases/millionbase.pgn'

class ChessBoardHandler(BasicHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self):
        self.render('../web/templates/board2.html')


class ChessQueryHandler(BasicHandler):
    def initialize(self, shared=None):
        self.shared = shared

    @staticmethod
    def run_background(func, callback, args=(), kwds=None):
        if not kwds:
            kwds = {}

        def _callback(result):
            IOLoop.instance().add_callback(lambda: callback(result))

        _workers.apply_async(func, args, kwds, _callback)

    # blocking task like querying to MySQL
    def blocking_task(self, n):
        # time.sleep(n)
        logging.info("called blocking task")
        # if not self.get_user_cookie_hash() in self.shared:
        #     self.start_cloud_engine()
        time.sleep(10)
        logging.info("done with blocking task!!")
        return n

    def on_complete_blocking_task(self, res):
        self.write("Blocking Task Complete {0}<br/>".format(res))
        logging.info("on_complete_blocking_task")
        self.finish()

    @asynchronous
    def get(self):
        try:
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

            #Blocking task test
            # self.run_background(self.blocking_task, self.on_complete_blocking_task, (10,))

            # moves = self.get_arguments("moves")
            # print self.get_argument("sorts")
            action = self.get_argument("action")
            requested_db = self.get_argument("db", default=None)
            # INDEX_DB = 'resources/polyglot_index.db'
            # DATABASE = 'resources/game.db'

            logging.info("requested_db: {0}".format(requested_db))

            fen = self.get_argument("fen", default=None)
            logging.info("fen : {0}".format(fen))
            callback = self.get_argument('callback', default='')

            records = []
            results = {}

            if action == "get_book_moves":
                logging.info("get book moves :: ")
                records = self.query_db(fen)

                # Reverse sort by the number of games and select the top 5, otherwise all odd moves will show up..
                records.sort(key=lambda x: x['games'], reverse=True)
                results = {"records": records[:5]}

            elif action == "get_games":
                logging.info("get_games :: ")

                records = self.query_db(fen)
                # Reverse sort by the number of games and select the top 5, for a balanced representation of the games
                records.sort(key=lambda x: x['games'], reverse=True)
                filtered_records = records[:5]

                filtered_game_offsets = []
                # Limit number of games to 10 for now
                for r in filtered_records:
                    for offset in r['pgn offsets']:
                        # print("offset: {0}".format(offset))
                        if len(filtered_game_offsets) >= 10:
                            break
                        filtered_game_offsets.append(offset)

                headers = self.chessDB.get_game_headers(self.chessDB.get_games(filtered_game_offsets))
                results = {"records": headers, "queryRecordCount": 1,
                           "totalRecordCount": len(headers)}

            elif action == "get_game_content":
                game_num = self.get_argument("game_num", default=0)
                if game_num:
                    print("game_num : {0}".format(game_num))
                #     pgn = self.get_game(db_index, int(game_num))
                #     # print "callback.."
                #     if callback:
                #         results = {"pgn": pgn}
                #
                #         jsonp="{jsfunc}({json});".format(jsfunc=callback,
                #         json=json_encode(results))
                #         self.set_header('Content-Type', 'application/javascript')
                #         self.write(jsonp)
                #     else:
                #         for i, p in enumerate(pgn):
                #             pgn[i] = re.sub(r'[^\x00-\x7F]+',' ', pgn[i])
                #         # print(pgn[1])
                #         results = {"pgn": pgn}
                #
                #         self.write(results)
                #     return

            if callback:
                jsonp = "{jsfunc}({json});".format(jsfunc=callback,
                    json=json_encode(results))
                self.set_header('Content-Type', 'application/javascript')
                self.write(jsonp)
            else:
                self.write(results)

            self.finish()



                # 1. "get_book_moves" (fen), limit?

                # print "starting fish"
                # sf.add_observer
                # sf.stop()
                # sf.position('startpos', moves)
                # sf.go(depth=1)
        except tornado.web.MissingArgumentError:
            pass

    def query_db(self, fen, max_offsets = 10):
        records = []
        # selecting DB happens now
        self.chessDB.open(MILLIONBASE_PGN)
        results = self.chessDB.find(fen, max_offsets = max_offsets)
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