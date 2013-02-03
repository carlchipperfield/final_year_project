import sys
import json
import re
sys.path.append("/app/share/python/site-packages")

from pymongo import MongoClient
from bson.objectid import ObjectId
from apiutils import *

id_pattern = re.compile('[0-91-f]{24}$')
sys.stdout = sys.stderr


class RestResource(object):

    supported_methods = []
    collection_name = None
    default_sort = None
    excluded_fields = None
    displayed_fields = None
    relations = {}

    def __init__(self):
        connection = MongoClient()
        self.db = connection.diagnostics

    @append_headers
    def GET(self, name=None):

        data = web.input()

        limit = get_limit(data)
        offset = get_offset(data)
        sort = get_sort(data)
        fields = get_fields(self.displayed_fields, self.excluded_fields)

        if name == None:
            name = self.collection_name
            output = self._find(name, {}, fields, sort, limit, offset)

        elif id_pattern.match(name):
            output = self._find_one(self.collection_name, name)

        else:
            url = name.split('/')
            id, name = url[0], url[1]

            if name in self.relations:
                collection_name = self.relations[name]['collection']

                query = {}
                query[self.relations[name]['field']] = id

                if 'filters' in self.relations[name]:
                    for filter in self.relations[name]['filters']:
                        if filter in data:
                            query[filter] = api_decode(data[filter])

                sort = [(self.relations[name]['sort'], 1)]

                output = self._find(collection_name, query, fields, sort, limit, offset)
            else:
                output = {}
                doc = self._find_one(self.collection_name, id)
                if name in doc:
                    output[name] = doc[name]

        return json.dumps(output)

    def _find(self, collection_name, query, fields, sort, limit, skip):
        collection = self.db[collection_name]
        docs = collection.find(spec=query, fields=fields, sort=sort, limit=limit, skip=skip)

        output = []
        for doc in docs:
            format_document_id(doc)
            output.append(doc)

        return {
            'total': docs.count(),
            collection_name: output
        }

    def _find_one(self, collection_name, doc_id):
        collection = self.db[collection_name]
        doc = collection.find_one(ObjectId(doc_id))
        format_document_id(doc)
        return doc

    @append_headers
    def DELETE(self, document_id):
        if "DELETE" in self.supported_methods:
            if id_pattern.match(document_id):

                collection = self.db[self.collection_name]
                result = collection.remove({"_id": ObjectId(document_id)})

                for key, value in self.relations.iteritems():
                    collection = self.db[value['collection']]
                    collection.remove({value['field']: document_id})

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
