import web
from pymongo import ASCENDING, DESCENDING


def append_headers(fn):
    def new(*args):
        web.header('Content-Type', 'application/json')
        return fn(*args)
    return new


def get_offset(data):
    try:
        return int(data['offset'])
    except (KeyError, ValueError):
        return 0


def get_limit(data):
    try:
        return int(data['limit'])
    except (KeyError, ValueError):
        return 0


def get_sort(data):
    sort = None

    if 'sort' in data and data['sort'] != '':
        sort_fields = data['sort'].split(',')
    else:
        return sort

    # If an id field is passed, convert it to _id
    try:
        index = sort_fields.index('id')
    except ValueError:
        pass
    else:
        sort_fields[index] = '_id'

    # Initially set the sort order for each field
    sort_order = [ASCENDING for i in range(len(sort_fields))]

    # If sort order has been provided overwrite the default
    if 'sortorder' in data:
        requested_sortorder = data['sortorder'].split(',')

        for index in range(len(sort_fields)):
            try:
                if requested_sortorder[index].lower() == 'desc':
                    sort_order[index] = DESCENDING
            except IndexError:
                break

    # Return a list of (field, order) tuples
    return zip(sort_fields, sort_order)


def get_fields(displayed_fields, excluded_fields):

    if excluded_fields is None and displayed_fields is None:
        return None

    fields = {}

    if displayed_fields != None:
        for field in displayed_fields:
            fields[field] = 1

    if excluded_fields != None:
        for field in excluded_fields:
            fields[field] = 0
    return fields


def format_document_id(document):
    doc_id = str(document['_id'])
    document['_id'] = doc_id


def api_decode(query):

    # Does the user want to split on OR
    values = query.split(' OR ')
    if len(values) > 1:
        return {'$in': values}
    return query
