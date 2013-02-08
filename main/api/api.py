import site
site.addsitedir('/app/python/lib/python2.7/site-packages')
import sys
sys.path.append("/app/share")
sys.path.append("/app/share/python/site-packages")
import web
sys.stdout = sys.stderr

from api.restresource import RestResource
from ni.network_traffic.snapshot import NetworkTrafficSnapshot


urls = [
    '/snapshot', 'Snapshot',
    '/snapshot/([0-9a-f]{24})', 'Snapshot',
    '/snapshot/([0-9a-f]{24}/[a-z_]+)', 'Snapshot',
    '/snapshotupload', 'SnapshotUpload'
]


class Snapshot(RestResource):
    collection_name = 'snapshots'
    supported_methods = ['GET', 'DELETE']
    relations = {
        'networkmessages': {
            'collection': 'networkmessages',
            'field': 'snapshot_id',
            'sort': 'index',
            'filters': [
                'method'
            ]
        }
    }


class SnapshotUpload:

    schema = {
        'title': {
            'type': 'string',
            'required': True
        },
        'description': {
            'type': 'string',
            'default': ''
        },
        'logfile_name': {
            'type': 'string',
            'required': True
        },
        'logfile_content': {
            'type': 'string',
            'required': True
        }
    }

    def __init__(self):
        self.snapshot = NetworkTrafficSnapshot()

    def POST(self):
        try:
            data = web.input()
            for field, schema in self.schema.iteritems():
                if field not in data:
                    if 'default' in self.schema[field]:
                        data[field] = self.schema[field]['default']
                    else:
                        web.badrequest()
                        return

        except AttributeError:
            pass
        else:
            # Process the logfile
            self.snapshot.upload(data['title'], data['description'], data['logfile_name'], data['logfile_content'])
            id = self.snapshot.save()
            self.snapshot.generate_statistics()
            return id


application = web.application(urls, globals()).wsgifunc()
