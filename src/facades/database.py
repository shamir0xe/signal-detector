from libs.PythonLibrary.mongo_db import Mongo

class CryptoDB:
    def __init__(self):
        self.host = "localhost"
        self.db = 'crypto'

    def do(self):
        return Mongo(self.host, self.db, '', '').get_db()

    @staticmethod
    def db():
        return CryptoDB().do()
