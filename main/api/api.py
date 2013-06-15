import site
site.addsitedir('/app/python/lib/python2.7/site-packages')
import sys
sys.path.append("/app/share")
sys.path.append("/app/share/python/site-packages")
import web
sys.stdout = sys.stderr

from api.restresource import RestResource
from ni.network_traffic.snapshot import NetworkTrafficSnapshot
from ni.network_traffic.snapshot import SIPDialogs, SipTransactions


# Define the URIs to access different resources
urls = [
    '/snapshot', 'Snapshot',
    '/snapshot/([0-9a-f]{24})', 'Snapshot',
    '/snapshot/([0-9a-f]{24}/[a-z_]+)', 'Snapshot',
    '/snapshot/([0-9a-f]{24}/[a-z_]+/[0-9a-f]{24})', 'Snapshot',
    '/snapshotupload', 'SnapshotUpload'
]


class Snapshot(RestResource):
    '''
        Snapshot class that inherits RestResource to extract data from database
        Can GET or DELETE snapshots
    '''
    collection_name = 'snapshots'
    supported_methods = ['GET', 'DELETE', 'PUT']
    relations = {
        'notes': {
            'collection': 'notes',
            'supported_methods': ['GET', 'DELETE'],
            'field': 'snapshot_id'
        },
        'networkmessages': {
            'collection': 'networkmessages',
            'supported_methods': ['GET'],
            'field': 'snapshot_id',
            'sort': 'index',
            'filters': [
                'method',
                'status',
                'call-id',
                'type',
                'destination',
                'source',
                'tagged'
            ]
        },
        'sipdialogs': {
            'collection': 'sipdialogs',
            'supported_methods': ['GET'],
            'field': 'snapshot_id',
            'filters': [
                'call_id',
                'sender',
                'receiver'
            ]
        },
        'siptransactions': {
            'collection': 'siptransactions',
            'supported_methods': ['GET'],
            'field': 'snapshot_id',
            'sort': 'utc'
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
            snapshot = NetworkTrafficSnapshot()
            snapshot.upload(data['title'], data['description'], data['logfile_name'], data['logfile_content'])
            snapshot_id = snapshot.save()

            # Process the statistics
            snapshot.generate_statistics()

            # Process the transactions
            transactions = SipTransactions()
            transactions.extract(snapshot_id)
            transactions.save()

            # Process the dialogs
            dialogs = SIPDialogs()
            dialogs.extract(snapshot_id)
            dialogs.save()

            return snapshot_id


application = web.application(urls, globals()).wsgifunc()
