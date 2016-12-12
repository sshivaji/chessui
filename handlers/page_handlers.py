import logging
import tornado
from handlers.basic_handler import BasicHandler
from tornado.escape import json_encode

class ChessBoardHandler(BasicHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self):
        self.render('../web/templates/board2.html')


class ChessQueryHandler(BasicHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self):
        try:
            # moves = self.get_arguments("moves")
            # print self.get_argument("sorts")
            action = self.get_argument("action")
            requested_db = self.get_argument("db", default=None)
            # INDEX_DB = 'resources/polyglot_index.db'
            # DATABASE = 'resources/game.db'

            fen = self.get_argument("fen", default=None)
            logging.info("fen : {0}".format(fen))
            callback = self.get_argument('callback', default='')

            records = []
            results = {}

            if action == "get_book_moves":
                m = {}
                m['pct'] = 100
                m['freq'] = 100
                m['wins'] = 100
                m['draws'] = 100
                m['losses'] = 0
                m['san'] = 'e4'
                record = {'move': m['san'], 'pct': "{0:.2f}".format(m['pct']), 'freq': m['freq'], 'wins': m['wins'],
                          'draws': m['draws'], 'losses': m['losses']}
                # print record
                records.append(record)
                results = {"records": records}

            elif action == "get_games":
                g = {}
                g['id'] = 1
                g['white'] = 'w'
                g['black'] = 'black'
                g['white_elo'] = '2500'
                g['black_elo'] = '2500'
                g['result'] = '1-0'
                g['date'] = ''
                g['event'] = 'Mock'
                g['site'] = 'Site'
                g['eco'] = 'eco'
                records.append({"id": g['id'], "white": g['white'], "white_elo": g['white_elo'], "black": g['black'],
                                "black_elo": g['black_elo'], "result": g['result'], "date": g['date'],
                                "event": g['event'], "site": g['site'],
                                "eco": g['eco']})

                results = {"records": records, "queryRecordCount": 1,
                           "totalRecordCount": 1}

            elif action == "get_game_content":
                game_num = self.get_argument("game_num", default=0)
                # if game_num:
                #     # print "game_num : {0}".format(game_num)
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



                # 1. "get_book_moves" (fen), limit?

                # print "starting fish"
                # sf.add_observer
                # sf.stop()
                # sf.position('startpos', moves)
                # sf.go(depth=1)
        except tornado.web.MissingArgumentError:
            pass