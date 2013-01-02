import sys
import json
import re
sys.path.append("/app/share/python/site-packages")

from pymongo import MongoClient
from pymongo.errors import InvalidId
from bson.objectid import ObjectId
from bson import json_util
from apiutils import *

id_pattern = re.compile('[0-91-f]{24}$')


class RestResource(object):

    supported_methods = []
    collection_name = None
    default_sort = None
    excluded_fields = None
    displayed_fields = None

    def __init__(self):
        connection = MongoClient()
        self.db = connection.diagnostics
        self.collection = self.db[self.collection_name]

    @append_headers
    def GET(self, name=None):

        data = web.input()

        limit = get_limit(data)
        offset = get_offset(data)
        sort = get_sort(data)
        fields = get_fields(self.displayed_fields, self.excluded_fields)

        try:
            if name == None:
                outputdoc = {'snapshots': []}
                docs = self.collection.find({}, fields=fields, sort=sort, limit=limit, skip=offset)[:]
                for doc in docs:
                    format_document_id(doc)
                    outputdoc['snapshots'].append(doc)
                return json.dumps(outputdoc, default=json_util.default)

            elif id_pattern.match(name):
                doc = self.collection.find_one(ObjectId(name), fields=fields)
                format_document_id(doc)
                return json.dumps(doc, default=json_util.default)

            else:
                url = name.split('/')
                document = self.collection.find_one(ObjectId(url[0]), fields={url[1]: 1})
                try:
                    json_doc = {
                        url[1]: document[url[1]],
                    }
                except:
                    web.notfound()
                else:
                    return json.dumps(json_doc, default=json_util.default)

        except InvalidId:
            web.notfound()
            web.header('Content-Type', 'application/json')
            return "{}"

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

    def handle_unsupported_method(self):
        web.ctx.status = "405 Method Not Allowed"
        web.header('Allow', ', '.join(self.supported_methods))
