import tornado.web
# from models import *
# from boto.s3.connection import S3Connection
# from boto.s3.connection import S3ResponseError


class BasicHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

