import sys
import json
import re
import time
sys.path.append("/app/share/python/site-packages")

from pymongo import MongoClient
from bson.objectid import ObjectId
from apiutils import *

id_pattern = re.compile('[0-91-f]{24}$')
sys.stdout = sys.stderr


class RestResource(object):
    '''
        Any class extending this class should provide a meta object that describes
        the associated collection, supported methods, relationships, default values

        REST Resources are identified using the following format
            api/<collection name>/<id>/<extention>
    '''
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
    def PUT(self, name=None):
        try:
            data = json.loads(web.data())
        except ValueError:
            web.badrequest()
            return

        url = name.split('/')

        if len(url) == 1:

            # Update the primary resource
            doc, id = self.collection_name, url[0]
            result = self.db[doc].update({'_id': ObjectId(id)}, {'$set': data})

        elif len(url) == 2:

            # Create a secondary resource
            doc, id = url[1], url[0]
            data[self.relations[doc]['field']] = id
            id = self.db[doc].insert(data)
            output = self._find_one(self.relations[doc]['collection'], id)
            return json.dumps(output)

        elif len(url) == 3:

            # Update a secondary resource
            doc, id = url[1], url[2]
            id = self.db[doc].update({'_id': ObjectId(id)}, {'$set': data})

        else:

            web.badrequest()

    @append_headers
    def GET(self, name=None):
        '''
            Provides a generic GET implementation that will:
                GET whole collection if no id supplied
                GET specfic resource if id is supplied
                GET a sub collection if id supplied with extention
        '''
        data = web.input() # Get any parameters sent with the HTTP request

        # Handle the rest params
        limit = get_limit(data)
        offset = get_offset(data)
        sort = get_sort(data)
        fields = get_fields(self.displayed_fields, self.excluded_fields)

        if name == None:
            # If only collection name identified, get the whole collection
            name = self.collection_name
            output = self._find(name, {}, fields, sort, limit, offset)

        elif id_pattern.match(name):
            # If a collection name + id is part of the url, retrieve the specific object
            output = self._find_one(self.collection_name, name)

        else:
            # If a collection name, id and extension provided
            url = name.split('/')

            if len(url) == 2:
                id, name, secid = url[0], url[1], None
            elif len(url) == 3:
                id, name, secid = url[0], url[1], url[2]

            if name in self.relations:
                # The field is stored in a separate db collection
                collection_name = self.relations[name]['collection']

                query = {}

                if secid:
                    output = self._find_one(collection_name, secid)

                else:
                    # Always use the id in the query
                    query[self.relations[name]['field']] = id

                    # Apply additional queries from the HTTP request
                    if 'filters' in self.relations[name]:
                        for filter in self.relations[name]['filters']:
                            if filter in data:
                                query[filter] = api_decode(data[filter])

                    # Override the default sort with that specified in the relation
                    if 'sort' in self.relations[name]:
                        sort = [(self.relations[name]['sort'], 1)]
                    else:
                        sort = None

                    output = self._find(collection_name, query, fields, sort, limit, offset)
            else:
                # The extension refers to a field within the object.
                # Attempt to find the field in the object returned from db
                # create a new object and fill with data if it exists,
                # else return the empty object
                output = {}
                doc = self._find_one(self.collection_name, id)
                if name in doc:
                    output[name] = doc[name]

        # Return the collection or object
        return json.dumps(output)

    @append_headers
    def DELETE(self, path):

        url = path.split('/')

        if len(url) == 1:
            resource_id = url[0]

            if "DELETE" in self.supported_methods:

                if id_pattern.match(resource_id):

                    # remove the main collection object
                    collection = self.db[self.collection_name]
                    result = collection.remove({"_id": ObjectId(resource_id)})

                    # Delete any collections stored separately
                    for key, value in self.relations.iteritems():
                        collection = self.db[value['collection']]
                        collection.remove({value['field']: resource_id})

                    # Output the end result
                    if result['n'] == 0:
                        web.notfound()
                    else:
                        web.ctx.status = "204 No Content"
                else:
                    web.badrequest()
            else:
                self.handle_unsupported_method(self.supported_methods)

        elif len(url) == 3:
            self.db.set_profiling_level(0)
            self.db.system.profile.drop()
            self.db.set_profiling_level(2)
            parent_resource_id, secondary_collection, resource_id = url[0], url[1], url[2]

            if id_pattern.match(parent_resource_id) and id_pattern.match(resource_id):
                if secondary_collection in self.relations:

                    # remove the resource
                    collection = self.db[secondary_collection]
                    result = collection.remove({"_id": ObjectId(resource_id)})

                    # Output the end result
                    if result['n'] == 0:
                        web.notfound()
                    else:
                        web.ctx.status = "204 No Content"
                else:
                    web.badrequest()
            else:
                web.badrequest()
        else:
            web.badrequest()

        docs = self.db.system.profile.find()
        for doc in docs:
            print doc

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

    def handle_unsupported_method(self, supported_methods):
        web.ctx.status = "405 Method Not Allowed"
        web.header('Allow', ', '.join(supported_methods))
