from collections import OrderedDict
from io import open
import os


class Document(object):
    def __init__(self, path):
        self.path = path
        self.content = ''
        self.meta = ''
        self.body = ''
        self.my_dict = OrderedDict()

    def process_markdown(self):
        self.get_content()
        self.split_content()
        self.build_request()
        return self.my_dict

    def get_content(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def split_content(self):
        self.meta = self.content.split('\n\n', 1)
        self.body = self.meta[1]
        self.meta = self.meta[0]
        self.meta = self.meta.split('\n')

    def build_request(self):
        for line in self.meta:
            key = line.split(':', 1)[0]
            value = line.split(':', 1)[1]
            self.my_dict[key.lower()] = value.rstrip()
        self.my_dict['body'] = self.body.rstrip()
        filename = os.path.basename(self.path)
        self.my_dict['url'] = os.path.splitext(filename)[0].rstrip()