import site
site.addsitedir('/app/python/lib/python2.7/site-packages')

import web
import sys
import json
import re
sys.path.append("/app/share/api")
sys.path.append("/app/share/python/site-packages")

from pymongo import MongoClient
from pymongo.errors import InvalidId
from bson.objectid import ObjectId
from bson import json_util
from rest_mongo_utils import append_headers
from ni.network_traffic.snapshot import NetworkTrafficSnapshot


urls = [
    '/snapshot/(.*)', 'Snapshot',
    '/snapshotupload', 'SnapshotUpload'
]

id_pattern = re.compile('^[0-9a-f]{24}$')


class RestResource(object):

    supported_methods = []
    collection_name = None

    def __init__(self):
        connection = MongoClient()
        self.db = connection.diagnostics
        self.collection = self.db[self.collection_name]  # to be assigned in the child classes

    @append_headers
    def GET(self, name):
        pass

    @append_headers
    def DELETE(self, document_id):
        if "DELETE" in self.supported_methods:
            if id_pattern.match(document_id):
                result = self.collection.remove({"_id": ObjectId(document_id)})
                if result['n'] == 0:
                    web.notfound()
                else:
                    web.ctx.status = "204 No Content"
            else:
                web.badrequest()
        else:
            self.handle_unsupported_method()

    def handle_unsupported_method(self):
        web.ctx.status = "405 Method Not Allowed"
        web.header('Allow', ', '.join(self.supported_methods))


class Snapshot(RestResource):

    collection_name = 'snapshots'
    supported_methods = ['GET', 'POST', 'DELETE']

    @append_headers
    def GET(self, name):
        try:
            if len(name) == 0:
                json_docs = []
                docs = self.collection.find({}, {'messages': 0})
                for doc in docs:
                    json_doc = json.dumps(doc, default=json_util.default)
                    json_docs.append(json_doc)
                doc = {'snapshots': json_docs}
                return doc
            else:
                doc = self.collection.find_one(ObjectId(name))
                del doc['_id']
                doc['id'] = name
                return json.dumps(doc, default=json_util.default)
        except InvalidId:
            web.notfound()
            web.header('Content-Type', 'application/json')
            return "{}"

    @append_headers
    def POST(self):
        try:
            data = json.loads(web.data())
        except ValueError:
            web.badrequest()
        else:
            # Validate the data

            # Lets insert the data
            snapshot_id = self.collection.insert(data)
            data['id'] = str(snapshot_id)
            del data['_id']

            # Lets send the response
            web.header('Content-Type', 'application/json')
            web.created()
            return data


class SnapshotUpload:

    def __init__(self):
        self.snapshot = NetworkTrafficSnapshot()

    def POST(self):
        try:
            title = web.input().title
            filename = web.input().logfile_name
            description = web.input().description
            content = web.input().logfile_content
        except AttributeError:
            pass
        else:
            # Write the logfile
            '''with open('/tmp/' + filename, 'w') as f:
                f.write(content)'''

            # Process the logfile
            self.snapshot.upload(title, description, filename, content)
            self.snapshot.save()


application = web.application(urls, globals()).wsgifunc()
