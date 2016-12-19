from tornado.web import url
from tornado.options import define, options, parse_config_file
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import wsgiref.simple_server

import base64
import uuid

import os
import logging

# from handlers import *
from handlers.page_handlers import *

# Constants
CONFIG_FILE = 'config.py'

# Options
define("autoreload", type=bool)
define("debug", type=bool)
define("db_path", type=str)
define("mode", type=str)
define("port", help="run on the given port", type=int)

parse_config_file(CONFIG_FILE)

shared = {}

cookie_secret = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "web/static"),
    "cookie_secret": cookie_secret,
    "autoescape": None,
    "mode": "server"
}

# Sqlalchemy imports
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.pool import QueuePool
# import sqlalchemy.pool as pool
# from models import game_database as game_db

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            url(r"/", ChessBoardHandler, dict(shared=shared)),
            url(r"/backend/query", ChessQueryHandler, dict(shared=shared)),
            # url(r"/cloud", ChessCloudHandler, dict(shared=shared)),
            # url(r"/user_login", UserLoginHandler),
            # url(r"/google_auth", GoogleOAuth2LoginHandler),
            # url(r"/oauth2callback", GoogleOAuth2LoginHandler),
            # url(r"/logout", LogoutHandler),
        ]

        app_settings = dict(
            debug=True,
            # hostname=hostname,
            port=options.port,
            autoreload=options.autoreload,
            serve_traceback=False,
            static_path=os.path.join(os.path.dirname(__file__), "static"),

            autoescape=None,
            cookie_secret=cookie_secret,
        )
        app_settings.update(settings)

        tornado.web.Application.__init__(self, handlers, **app_settings)
        # engine = create_engine(
        #     options.db_path, convert_unicode=True, echo=options.debug,
        #     connect_args={'check_same_thread': False})
        # game_db.init_db(engine)

        # self.db = scoped_session(sessionmaker(bind=engine))
        self.mode = options.mode
        self.opts = options

app = Application()

if __name__ == "__main__":
    # application.listen(9999)
    # tornado.ioloop.IOLoop.instance().start()

    wsgi_app = tornado.wsgi.WSGIAdapter(Application())
    server = wsgiref.simple_server.make_server('', options.port, wsgi_app)
    server.serve_forever()

    # http_server = tornado.httpserver.HTTPServer(Application())
    # http_server.listen(options.port)
    # logger = logging.getLogger('tcpserver')
    # logger.info("Starting server at {0}".format(options.port))
    # tornado.ioloop.IOLoop.instance().start()