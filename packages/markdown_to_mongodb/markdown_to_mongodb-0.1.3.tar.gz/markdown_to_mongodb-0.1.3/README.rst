===================
Markdown to MongoDB
===================

This package converts a directory of markdown files and inserts their contents into a provided MongoDB instance.

Usage
=====
::
    #!/usr/bin/env python

    from markdown_to_mongodb import Db

    my_db = Db(ip, port, collection_name)
    my_db.convert(markdown_directory)

Command Line Usage
==================

    python Db.py "localhost" 27017 "collection_name" "markdown_directory"

