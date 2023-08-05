# -*- coding: utf-8 -*-
from pymongo import MongoClient
import os
from Document import Document
import argparse


class Db(object):
    def __init__(self, ip='localhost', port=27017, collection_name=''):
        self.collection_name = collection_name
        self.client = MongoClient(ip, port)
        self.db = self.client[self.collection_name]

    def try_catch(func):
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, e:
                print str(e)
        return wrapped

    @try_catch
    def insert(self, my_json):
        self.db[self.collection_name].insert_one(my_json)
        return True

    @try_catch
    def exists(self, url):
        db_page = self.db[self.collection_name].find_one({'url': url})
        if db_page is not None and url in db_page['url']:
            return True
        return False

    def convert(self, folder):
        for root, dirs, files in os.walk(folder):
            for file_ in files:
                if file_.endswith('.md'):
                    my_doc = Document(os.path.join(root, file_))
                    data = my_doc.process_markdown()
                    self.insert(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="The ip address of your mongodb instance. Default localhost.")
    parser.add_argument("port", type=int, help="The port of your mongodb instance. Default 27017.")
    parser.add_argument("collection", help="The name of the collection you want to insert your documents into.")
    parser.add_argument("directory", help="The directory containing your markdown files to insert.")
    args = parser.parse_args()

    collection_name = args.collection
    markdown_directory = args.directory
    ip = args.ip
    port = args.port
    my_db = Db(ip, port, collection_name)
    my_db.convert(markdown_directory)